# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import zipfile
from StringIO import StringIO
from contextlib import closing

import xmltodict
from scrapy import spiders

from kingsnake.items import Deputado


class DeputadosSpider(spiders.XMLFeedSpider):
    name = 'deputados'
    allowed_domains = ['www.camara.gov.br']
    itertag = 'sessoesDiscursos'
    iterator = 'iternodes'

    start_urls = [('http://www.camara.leg.br'
                   '/internet/deputado/DeputadosXML_52a55.zip')]

    def parse(self, response):
        with closing(StringIO(response.body)) as response_file:
            with closing(zipfile.ZipFile(response_file)) as response_zip_file:
                with closing(response_zip_file.open('Deputados.xml')) as xml_deputados:
                    deputados = xml_deputados.read()

        deputados = xmltodict.parse(deputados)
        deputados = deputados['orgao']['Deputados']['Deputado']

        for d in deputados:
            yield Deputado(**dict(
                uf=d.get('UFEleito'),
                nome=d.get('nomeParlamentar'),
                ide_cadastro=d.get('ideCadastro'),
                num_legislatura=d.get('numLegislatura'),
                partido=d.get('LegendaPartidoEleito'),
            ))
