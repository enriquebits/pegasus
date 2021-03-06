# -*- coding: utf-8 -*-
"""Sample controller module"""

# turbogears imports
from tg import expose

from tg import redirect, validate, flash
#from tg.i18n import ugettext as _
#from tg import predicates

# project specific imports
from pegasus.lib.base import BaseController

from pegasus import model
""" con DBSession se puede acceder a las tablas para hacer consultas, ediciones, altas, bajas, etc """
from pegasus.model import DBSession, metadata
""" Hay que importar las clases de todas las tablas que queramos ocupar """
from pegasus.model import SampleModel

""" esto se usa para mostrar logs en la consola (como en post_form) """
# log imports
import re
import logging
log = logging.getLogger(__name__)


class SampleController(BaseController):
    
    @expose('pegasus.templates.sample_index')
    def index(self):
        return dict(page='Index de SampleController')


    """ Los siguientes dos controladores se usan para la página de la forma. """


    """El primer controlador (form) se encarga de mostrar el template indicado al usuario"""
    @expose('pegasus.templates.sample_form')
    def form(self):
        # diccionario en el que se almacenarán todos los valores que se le quieran pasar a la template
        values = dict()
        # crear una lista con opciones para llenar un select
        values['options'] = ('Opcion Uno', 'Opcion Dos', 'Opcion Tres')
        return dict(page='Forma de Prueba', values=values)


    """ Este controlador se usa unicamente para procesar lo que el usuario mande a través de la forma.
    Estos valores llegan en forma de un diccionario de nombre keywords (**kw). Como este controlador solo
    procesa información no va a mostrar ningún template (expose está vacío), sino que cuando termine de
    procesar va a redireccionar al usuario a la página after_form """
    @expose()
    def post_form(self, **kw):
        # con esta función se muestra lo que está recibiendo el método de la forma
        log.debug("Recibiendo post_form\n%s", kw)
        # para sacar estos valores podemos usar la sig función:
        # kw.get(name_que_se_puso_en_el_html, valor_por_default_si_no_se_encuentra_la_variable_xD)
        name = kw.get('name', None) 
        description = kw.get('description', None) 
        select = kw.get('type', None)  
        radio = kw.get('optionsRadios', None)
        checkbox = kw.get('checkbox', 'off')    
        # aquí se procesa todo lo que haya mandado el usuario, como por ej, se puede dar de alta en la BD:
        # como en ORM relacionas cada registro de tus tablas con un objeto, para crear nuevos registros es necesario crear nuevos objetos:
        # (lo ideal aquí es hacer validaciones, pero ahorita no importa mucho jajaja)
        sample = SampleModel()
        # luego llenamos cada atributo con lo que recibimos de la forma:
        sample.name = name
        sample.description = description
        sample.checkbox = True if checkbox == 'on' else False
        sample.select_option = select
        sample.radio_option = radio
        # finalmente, ya podemos dar de alta nuestro objeto en la sesión temporal:
        model.DBSession.add(sample)
        # y con flush escribimos todos los cambios en la base de datos
        model.DBSession.flush()
        # a partir de aquí, la instancia 'sample' ya tiene un id asignado,
        # por lo que si queremos usarlo en la siguiente pantalla basta con mandar ese id y hacer una consulta:
        id = sample.id
        # finalmente se redirecciona a la página siguiente
        redirect('after_form', id=id)

    @expose('pegasus.templates.after_form')
    def after_form(self, **kw):
        log.debug("Recibiendo after form \n%s", kw)
        # recibimos el id del registro que se dio de alta en la forma anterior, por lo que
        # podemos consultarlo en la BD para mostrar su información:
        id = kw.get('id', None)
        sample = SampleModel.by_id(id)
        # le mandaré valores a la template nada más para mostrar usos de genshi:
        values = dict()
        values['name'] = sample.name
        values['description'] =  sample.description

        select = sample.select_option
        if select is None:
            values['opcion_select'] = 'Nada'
        else:
            values['opcion_select'] = u'Escogiste la opción ' + select

        checkbox = sample.checkbox
        if checkbox :
            values['checkbox'] = 'Marcaste el checkbox'
        else:
            values['checkbox'] = 'No marcaste el checkbox'

        radio = sample.radio_option
        if radio is None:
            values['opcion_radio'] = 'Nada'
        else:
            values['opcion_radio'] = u'Escogiste la opción ' + radio

        return dict(page='Resultado', values=values)
