# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy import spiders, log


class TeorDiscursosSpider(spiders.Spider):
    name = 'teordiscursos'
    limit = None
    start_urls = ['http://labhackercd.net']

    def __init__(self, *args, **kwargs):
        super(TeorDiscursosSpider, self).__init__(*args, **kwargs)

        if not isinstance(self.limit, int):
            try:
                self.limit = int(self.limit)
            except:
                self.log('Ignoring invalid limit "{0}"'.format(self.limit), log.ERROR)
                self.limit = None

    def _speech_url(self, item):
        url = ('http://www.camara.gov.br/SitCamaraWS/'
                'SessoesReunioes.asmx/obterInteiroTeorDiscursosPlenario'
                '?codSessao={sessao}&numOrador={numeroOrador}'
                '&numQuarto={numeroQuarto}&numInsercao={numeroInsercao}')
        return url.format(**item)

    def parse(self, response):
        # TODO

        pipeline = DiscursosMongoDBPipeline()
        pipeline.open_spider(self)

        speeches = pipeline.collection.find({
            '$or': [
                {'files': {'$size': 0}},
                {'files': {'$exists': False}},
            ],
        })

        if self.limit:
            speeches = speeches.limit(self.limit)

        for speech in speeches:
            yield speech
