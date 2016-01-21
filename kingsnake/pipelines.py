# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from StringIO import StringIO as BytesIO

import xmltodict
from pymongo import ASCENDING
from scrapy.http import Request
from scrapy.contrib.pipeline.files import FilesPipeline
from scrapy.utils.misc import md5sum
from scrapy_mongodb import MongoDBPipeline

from kingsnake.items import Discurso, Deputado


class ItemSpecificPipelineMixin(object):
    """Mixin for pipelines which are specific to some items.
    You just reimplement `should_process_item` to return
    weather or not the specific *item* should be processed.
    """

    def should_process_item(self, item, spider):
        return True

    def process_item(self, item, spider):
        print('Processing item: ', self.__class__.__name__, item.__class__.__name__, self.should_process_item(item, spider))
        if not self.should_process_item(item, spider):
            return item
        else:
            return super(ItemSpecificPipelineMixin, self).process_item(item, spider)


class DiscursoMongoDBPipeline(ItemSpecificPipelineMixin, MongoDBPipeline):

    def should_process_item(self, item, spider):
        return isinstance(item, Discurso)

    def configure(self):
        super(DiscursoMongoDBPipeline, self).configure()
        self.config = dict(self.config)
        self.config['collection'] = 'discursos'
        self.config['unique_key'] = [
            ('sessao', ASCENDING),
            ('numeroOrador', ASCENDING),
            ('numeroQuarto', ASCENDING),
            ('numeroInsercao', ASCENDING),
        ]


class DeputadoMongoDBPipeline(ItemSpecificPipelineMixin, MongoDBPipeline):

    def should_process_item(self, item, spider):
        return isinstance(item, Deputado)

    def configure(self):
        super(DeputadoMongoDBPipeline, self).configure()
        self.config = dict(self.config)
        self.config['collection'] = 'deputados'


class TeorDiscursoPipeline(ItemSpecificPipelineMixin, FilesPipeline):

    URL_TEMPLATE = ('http://www.camara.gov.br/SitCamaraWS/'
                    'SessoesReunioes.asmx/obterInteiroTeorDiscursosPlenario'
                    '?codSessao={sessao}&numOrador={numeroOrador}'
                    '&numQuarto={numeroQuarto}&numInsercao={numeroInsercao}')

    def should_process_item(self, item, spider):
        return isinstance(item, Discurso) and not item.get('files', [])

    def get_media_requests(self, item, info):
        return [Request(self.URL_TEMPLATE.format(**item))]

    def file_downloaded(self, response, request, info):
        # The downloaded file is a XML file which stores the actual RTF file as
        # a base64 encoded string. Here we extract and decode that value.
        data = xmltodict.parse(response.body)
        data = data.get('sessao').get('discursoRTFBase64')
        data = base64.b64decode(data)

        # And here we basically do the same as super, but using our
        # decoded data instead of `response.body`
        path = self.file_path(request, response=response, info=info)
        buf = BytesIO(data)
        self.store.persist_file(path, buf, info)
        checksum = md5sum(buf)
        return checksum

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.FILES_RESULT_FIELD in item.fields:
            item[self.FILES_RESULT_FIELD] = [x for ok, x in results if ok]
        return item

    def file_path(self, request, response=None, info=None):
        # XXX `super.file_path` appends the request's query string
        # into the filename. Now we must remove it.
        path = super(TeorDiscursoPipeline, self).file_path(request, response, info)
        basename, extension = path.split('.', 1)
        return '.'.join([basename, 'rtf'])
