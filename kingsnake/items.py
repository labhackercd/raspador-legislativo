# -*- coding: utf-8 -*-
import scrapy


class Discurso(scrapy.Item):
    sessao = scrapy.Field()
    faseSessao = scrapy.Field()

    horaInicioDiscurso = scrapy.Field()

    ufOrador = scrapy.Field()
    nomeOrador = scrapy.Field()
    numeroOrador = scrapy.Field()
    partidoOrador = scrapy.Field()

    numeroQuarto = scrapy.Field()
    numeroInsercao = scrapy.Field()

    sumario = scrapy.Field()

    files = scrapy.Field()


class Deputado(scrapy.Item):
    uf = scrapy.Field()
    nome = scrapy.Field()
    partido = scrapy.Field()
    ide_cadastro = scrapy.Field()
    num_legislatura = scrapy.Field()
