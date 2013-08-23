# -*- encoding: utf8 -*-
import 		urllib2
import 		json
import		functools
from 		nagare 			import 	presentation, component, ajax, wsgi
from   		nagare.namespaces 	import 	xhtml
from 		collections		import 	namedtuple
import 		os


NBSP = u'\N{NO-BREAK SPACE}'

d_labels 	= {
		   'appcodes'		: '''Code application''',
		   'aeras'		: '''Zone reseau''',
		   'envs'		: '''Environnement''',
		   'appcomps'		: '''Type d'application''',
	           'num_components'	: '''Instance''',
           	  }

RootWS = namedtuple( 'RootWS', [ 'id_', 'URL' ] )

class Cloudmgrnuiws(object):

    _dict_rootWS       = {
                           #'/CLOUDMRGWS'       : 'http://10.161.113.60:8080/cloudmgrws',
                           #'/CLOUDMRGWS2'     : 'http://10.161.113.60:8080/cloudmgrws',
                          }


    def get_list_rootWS( self ):
        return sorted( 
            [ 
             RootWS( id_, URL ) 
             for id_, URL 
             in self._dict_rootWS.iteritems()
            ], 
            key = lambda WS: WS.id_
        ) or [ RootWS( 'NO WEBSERVICE', '' ) ]
    list_rootWS 	= property( get_list_rootWS, None, None, None )

    def __init__( self ):
        self.reinit_levels()


    def reinit_levels( self, rootWS = None ):
        if rootWS:
            self._selected_levels	= self._processed_levels 	= [ rootWS ]
        else:
            self._processed_levels 	= [ self.list_rootWS[ 0 ] ]
            #Fonctionnalite qui pourrait etre rempalcer par un rechargement des
            #d'un etat de deriere utilisation
            #self._selected_levels 	= [ self.list_rootWS[ 0 ], 'X04', 'VILLE', 'R7', 'TOMCAT', '0002' ]
            self._selected_levels 	= [ self.list_rootWS[ 0 ] ]

    def get_processed_WSURL( self ):
        if len( self._selected_levels ) == 1:
            return self._selected_levels[ 0 ].URL
        else:
            return '/'.join( [ self._processed_levels[ 0 ].URL ] + self._processed_levels[ 1: ] )
    processed_WSURL		= 	property( get_processed_WSURL, None, None, None )

    def get_selected_WSURL( self ):
        return '/'.join( [ self._selected_levels[ 0 ].URL ] + self._selected_levels[ 1: ] )
    selected_WSURL             =       property( get_selected_WSURL, None, None, None )


def force_wrapper_to_generate( force = True ):
    def wrapper( f ):
        @functools.wraps( f )
        def wrapped( self, h, *args ):
            h.wrapper_to_generate = force
            return f( self, h, *args )
        return wrapped
    return wrapper

def generate_background_class():
    colors = [ 'light', 'dark' ]
    i_colors = colors.__iter__()
    while True:
        try:
            yield i_colors.next()
        except Exception, e:
            i_colors = colors.__iter__()

@presentation.render_for( Cloudmgrnuiws )
@force_wrapper_to_generate( True )
def render(self, h, *args):

    h.head.css_url(
        'cloudmgrnuiws.css'
    )

    h.head.css_url(
        ajax.YUI_PREFIX + '/container/assets/skins/sam/container.css' 
    )

    h.head.javascript_url( 
        ajax.YUI_PREFIX + '/yahoo-dom-event/yahoo-dom-event.js'
    )

    h.head.javascript_url( 
        ajax.YUI_PREFIX + '/connection/connection-min.js'
    )

    h.head.javascript_url( 
        ajax.YUI_PREFIX + '/animation/animation-min.js'
    )

    h.head.javascript_url( 
        ajax.YUI_PREFIX + '/dragdrop/dragdrop-min.js'
    )

    h.head.javascript_url(
        ajax.YUI_PREFIX + '/container/container-min.js'
    )

    h.head.javascript_url(
        ajax.YUI_PREFIX + '/json/json-min.js'
    )

    if h.__class__ <> xhtml.AsyncRenderer:
        with h.body(class_='yui-skin-sam'):
            h << component.Component( self ).render( xhtml.AsyncRenderer( h ) )
        return h.root

    with h.div( class_ = 'wsnui_navigator first table ;' ):
        with h.div( class_ = 'wsnui_navigator row ;' ):
            h << component.Component( self, model = 'WS_COLUMN' ).render( xhtml.AsyncRenderer( h ) )

    return h.root

@presentation.render_for( Cloudmgrnuiws, model = 'WS_COLUMN' )
@force_wrapper_to_generate( True )
def render(self, h, *args):

    background_color = generate_background_class()

    with h.div( class_ = 'wsnui_navigator cell ;' ):
        with h.div( class_ = 'wsnui_navigator data title ;' ):
            h << 'Web Service'
        with h.div( class_ = 'wsnui_navigator datas ;' ):

            for ws in self.list_rootWS:
                 def reinit_levels( ws = ws ):
                      self.reinit_levels( ws )

                 h << h.a(
                     h.div(
                         ws.id_,
                         class_ = 'wsnui_navigator data %s' % background_color.next() + ( ' selected' if ws.id_ == self._selected_levels[ 0 ].id_ else '' )
                     )
                 ).action( reinit_levels )

    with h.div( class_ = 'wsnui_navigator cell ;' ):
        with h.div( class_ = 'wsnui_navigator table ;' ):
	    with h.div( class_ = 'wsnui_navigator row ;' ):
                h << component.Component( self, model = 'ELEMENT_COLUMN' ).render( xhtml.AsyncRenderer( h ) )

    return h.root

def process_WSURL( WSURL ):
   if WSURL:
       try:
           f       	= urllib2.urlopen( WSURL )
           return json.load( f )
       except:
           return 	{
               'is_ok'			: False,
               'accepted_commands'	: [],
               'information_message'	: '',
               'next'			: {},
               'execution'		: {
                   'steps'		: [],
                   'has_been_executed'	: False,
               },
               'datas'			: []
           }
   else:
       return 	{
           'is_ok'			: False,
           'accepted_commands'		: [],
           'information_message'	: '',
           'next'			: {},
           'execution'			: {
               'steps'			: [],
               'has_been_executed'	: False,
           },
           'datas'			: []
       }

@presentation.render_for( Cloudmgrnuiws, model = 'ELEMENT_COLUMN' )
@force_wrapper_to_generate( True )
def render(self, h, *args):

    background_color = generate_background_class()

    # Test sur la prensece d'une action dans le path
    if not reduce( 
        lambda e1, e2: e1 or e2,
        [ e.startswith( '@' ) for e in self._processed_levels[ 1: ] ] if len( self._processed_levels ) > 1 else [ False, False ]
    ):
        r	= process_WSURL( self.processed_WSURL )

        with h.div( class_ = 'wsnui_navigator cell ;' ):

            for type_object, objects in r[ 'next' ].iteritems():
                with h.div( class_ = 'wsnui_navigator data title ;' ):
                    h << d_labels.get( type_object, type_object )

                with h.div( class_ = 'wsnui_navigator datas x2' if not r[ 'accepted_commands' ]  else 'wsnui_navigator datas'  ):
                    for o in objects:

                        def update_levels( 
                            o = o, 
                            selected_levels 	= self._selected_levels[ : ] if self._selected_levels == self._processed_levels else self._processed_levels[ : ], 
                            processed_levels 	= self._processed_levels[ : ] 
                        ):
                            self._selected_levels   = selected_levels[ : ]
                            self._processed_levels  = processed_levels[ : ]
                            self._selected_levels.append( o )

                        if o == self._selected_levels[ len( self._processed_levels ) - len( self._selected_levels ) ]:
                            h << h.a(
                                h.div(
                                    component.Component( Entity( o, self.processed_WSURL[ : ] ), model = 'SELECTED' ).render( xhtml.AsyncRenderer( h ) ),
                                    class_ = 'wsnui_navigator data %s selected' % background_color.next()
                                )
                            ).action( update_levels )

                        else:
                            h << h.a(
                                h.div(
                                    component.Component( Entity( o ) ).render( xhtml.AsyncRenderer( h ) ),
                                    class_ = 'wsnui_navigator data %s' % background_color.next()
                                )
                            ).action( update_levels )

            if r[ 'accepted_commands' ]:

                with h.div( class_ = 'wsnui_navigator action title ;' ):
                    h << 'Actions'

                with h.div( class_ = 'wsnui_navigator actions x2 ;' if not r[ 'next' ] else 'wsnui_navigator actions' ):
                    for action in r[ 'accepted_commands' ]:

                        def update_levels(
                            action = action,
                            selected_levels    	 	= self._selected_levels[ : ] if self._selected_levels == self._processed_levels else self._processed_levels[ : ],
                            processed_levels    	= self._processed_levels[ : ]
                        ):
                            self._selected_levels   	= selected_levels[ : ]
                            self._processed_levels  	= processed_levels[ : ]
                            self._selected_levels.append( action )

                        if action == self._selected_levels[ len( self._processed_levels ) - len( self._selected_levels ) ]:
                            with h.div( class_ = 'wsnui_navigator action %s selected' % background_color.next() ):
                                with h.div( class_ = 'wsnui_action table' ):
                                    with h.div( class_ = 'wsnui_action row' ):
                                        with h.a( class_ = 'wsnui_action cell actionname_aera' ) as a:
                                            h << action
                                            a.action( update_levels )
                                        h << component.Component( Action( self.selected_WSURL[ : ] ), model = 'READY_TO_RUN' ).render( xhtml.AsyncRenderer( h ) )
                                     
                        else:
                            with h.div( class_ = 'wsnui_navigator action %s' % background_color.next() ):
                                with h.a( class_ = 'wsnui_action table' ) as a:
                                    with h.div( class_ = 'wsnui_action row' ):
                                        with h.div( class_ = 'wsnui_action cell actionname_aera' ):
                                            h << action
                                        h << component.Component( Action( self.selected_WSURL[ : ] ) ).render( xhtml.AsyncRenderer( h ) )
                                    a.action( update_levels )

    else:
        print '''Gerer les parametres de fonction'''

    if len( self._selected_levels ) <> 1 and ( self._selected_levels <> self._processed_levels ):
	self._processed_levels = self._selected_levels[ :len( self._processed_levels ) + 1 ]
        with h.div( class_ = 'wsnui_navigator cell ;' ):
            with h.div( class_ = 'wsnui_navigator table ;' ):
	        with h.div( class_ = 'wsnui_navigator row ;' ):
                    h << component.Component( self, model = 'ELEMENT_COLUMN' ).render( xhtml.AsyncRenderer( h ) )

    return h.root


class Entity( object ):

    def __init__( self, entity, processed_WSURL = '' ):
        self._entity		= entity
        if processed_WSURL:
            self._current_WSURL	= processed_WSURL + '/' + self._entity
        else:
            self._current_WSURL = processed_WSURL

@presentation.render_for( Entity )
@force_wrapper_to_generate( True )
def render(self, h, *args):
    with h.div( class_ = 'wsnui_entity table' ):
        with h.div( class_ = 'wsnui_entity row' ):
            with h.div( class_ = 'wsnui_entity cell entity_name' ):
                h << self._entity 
            with h.div( class_ = 'wsnui_entity cell status' ):
                with h.div( class_ = 'wsnui_entity status_spacer' ):
                    h << NBSP
    return h.root

@presentation.render_for( Entity, model = 'SELECTED' )
@force_wrapper_to_generate( True )
def render(self, h, *args):
    with h.div( class_ = 'wsnui_entity table' ):
        with h.div( class_ = 'wsnui_entity row' ):
            with h.div( class_ = 'wsnui_entity cell entity_name' ):
                h << self._entity
            with h.div( class_ = 'wsnui_entity cell status' ):
                with h.div( class_ = 'wsnui_entity status_spacer' ):
                    if u'@STATUS' in process_WSURL( self._current_WSURL )[ 'accepted_commands' ]:
                        h << component.Component( StatusChecker( self._current_WSURL[ : ] + '/@STATUS' ) ).render( xhtml.AsyncRenderer( h ) )
                    else:
                        h << NBSP
    return h.root


class Action( object ):

    def __init__( self, selected_WSURL ):
        self._selected_WSURL	= selected_WSURL
        self._result_WSURL	= {}
        self._id_modal		= None

@presentation.render_for( Action )
@force_wrapper_to_generate( True )
def render(self, h, comp, *args):

    if self._id_modal:
        h << h.script(
'''
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.hide() ;
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.destroy() ;
'''.format( ID_MODAL = self._id_modal )
        )
        self._id_modal = None

    with h.div( class_ = 'wsnui_action cell run_aera' ):
        with h.div( class_ = 'wsnui_action run_aera_spacer' ):
            h << NBSP

    return h.root

@presentation.render_for( Action, model = 'READY_TO_RUN' )
@force_wrapper_to_generate( True )
def render(self, h, comp, *args):

    if self._id_modal:
        h << h.script( 
'''
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.hide() ;
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.destroy() ;
'''.format( ID_MODAL = self._id_modal )
        )

        self._id_modal = None

    with h.div( class_ = 'wsnui_action cell run_aera' ):
        with h.a( class_ = 'wsnui_action run_aera_spacer ready_to_run' ) as a:
            h << 'exec'
            a.action( lambda comp=comp: comp.becomes( comp, 'RUNNING' ) )
    return h.root

@presentation.render_for( Action, model = 'RUNNING' )
@force_wrapper_to_generate( True )
def render(self, h, comp, *args):

    partial_WSURL 	= '/' + '/'.join( self._selected_WSURL.split( '/' )[ 3: ] )

    self._id_modal	= h.generate_id( 'running_modal' )
    id_wait		= h.generate_id( 'id_wait' )

    def call_selected_WSURL( comp = comp ):
        self._result_WSURL 	= process_WSURL( self._selected_WSURL )
        comp.becomes( comp, model = 'ENDED' )

    u = ajax.Update(
        lambda r, comp = comp: comp.render( r ),
        call_selected_WSURL
    )

    format_params = {
       'ID_MODAL'	: self._id_modal, 
       'ID_WAIT'	: id_wait,
       'PARTIAL_WSURL'	: partial_WSURL,
       'ACTION'		: u.generate_action( 2, h )
    }

    with h.div( class_ = 'wsnui_action cell run_aera' ):
        with h.div( class_ = 'wsnui_action run_aera_spacer running' ):
            h << 'running...'
            h << h.div( id = format_params[ 'ID_MODAL' ] )

            with h.div( id = format_params[ 'ID_WAIT' ], style = 'display: none ;' ):
                with h.div( style = 'text-align : center ;' ):
                    h << h.img( src='/static/cloudmgrnuiws/img/rel_interstitial_loading.gif' )

            h << h.script( '''
YAHOO.namespace("mdp.cloudmgr.nuiws.{ID_MODAL}") ;
var content = document.getElementById( '{ID_MODAL}' ) ;
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait = '''.format( **format_params ) +
'''
    new YAHOO.widget.Panel(
        'wait',  
        { 
         width		: '30em', 
         fixedcenter	: true, 
         close		: false, 
         draggable	: false, 
         zindex		: 4,
         modal		: true,
         visible	: true
        } 
    );
''' +
'''
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.setHeader( '{PARTIAL_WSURL}...' );
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.setBody( document.getElementById( '{ID_WAIT}' ).innerHTML );
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.render( document.body );

// Appel Asynchrone
{ACTION} ;
'''.format( **format_params ),
	        type = 'text/javascript"'
            )

    return h.root

@presentation.render_for( Action, model = 'ENDED' )
@force_wrapper_to_generate( True )
def render(self, h, comp, *args):

    h << h.script( 
'''
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.hide() ;
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.destroy() ;
'''.format( ID_MODAL = self._id_modal )
    )

    def call_close( comp = comp ):
        comp.becomes( comp, model = 'READY_TO_RUN' )

    u = ajax.Update(
        lambda r, comp = comp: comp.render( r ),
        call_close
    )

    self._id_modal      = h.generate_id( 'running_modal' )
    id_close		= h.generate_id( 'close' )
    id_status		= h.generate_id( 'status' )

    format_params = {
       'ID_MODAL'       : self._id_modal,
       'ID_STATUS'      : id_status,
       'ID_CLOSE'       : id_close,
    }

    result_WSURL = ResultWSURL( self._selected_WSURL, self._result_WSURL )

    with h.div( class_ = 'wsnui_action cell run_aera' ):
        with h.div( class_ = 'wsnui_action run_aera_spacer running' ):
            h << component.Component( result_WSURL )

            h << h.div( id = format_params[ 'ID_MODAL' ] )

            with h.div( id = format_params[ 'ID_STATUS' ], style = 'display: none ;' ):
                h << component.Component( result_WSURL, model = 'COLORED_LIGHT' )

            with h.div( id = format_params[ 'ID_CLOSE' ], style = 'display: none ;' ):
                h << h.a( 'Fermer', class_ = 'wsnui_status close' ).action( call_close )

            h << h.script( '''
YAHOO.namespace('mdp.cloudmgr.nuiws.{ID_MODAL}' ) ;
var content = document.getElementById( '{ID_MODAL}' ) ;
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait = '''.format( **format_params ) +
'''
    new YAHOO.widget.Panel(
        'wait',
        {
         width          : '30em',
        fixedcenter    : true,
         close          : false,
         draggable      : false,
         zindex         : 4,
         modal          : true,
         visible        : true
        }
   );
'''
            )

            h << h.script(
'''
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.setHeader( 'STATUT' );
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.setBody( document.getElementById( '{ID_STATUS}' ).innerHTML );
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.setFooter( document.getElementById( '{ID_CLOSE}' ).innerHTML );
YAHOO.mdp.cloudmgr.nuiws.{ID_MODAL}.wait.render( document.body );
'''.format( **format_params )
            )

    return h.root

class ResultWSURL( object ):
    def __init__( self, selected_WSURL, result_WSURL ):
        self._selected_WSURL 	= selected_WSURL
        self._result_WSURL 	= result_WSURL

@presentation.render_for( ResultWSURL )
@force_wrapper_to_generate( False )
def render(self, h, comp, *args):

    h << str( 'OK' if self._result_WSURL[ 'is_ok' ] else 'KO' )

    return h.root

@presentation.render_for( ResultWSURL, model = 'COLORED_LIGHT' )
@force_wrapper_to_generate( False )
def render(self, h, comp, *args):

    with h.div( class_ = 'wsnui_status colored_light %s' % ( 'ok' if self._result_WSURL[ 'is_ok' ] else 'ko' ) ):
        h << component.Component( self )

    return h.root


class StatusChecker( object ):
     def __init__( self, status_WSURL ):
         self._status_WSURL = status_WSURL
         self._result_WSURL = {}

@presentation.render_for( StatusChecker )
@force_wrapper_to_generate( True )
def render(self, h, comp, *args):

    def check_status( comp = comp ):
        self._result_WSURL      = process_WSURL( self._status_WSURL )
        comp.becomes( comp, model = 'CHECKED' )

    u = ajax.Update(
        lambda r, comp = comp: comp.render( r ),
        check_status
    )

    with h.div( class_ ='checker checking' ):
        h << 'checking...'

    h << h.script(
        u.generate_action( 2, h )
    )

    return h.root

@presentation.render_for( StatusChecker, model = 'CHECKED' )
@force_wrapper_to_generate( True )
def render(self, h, comp, *args):

    def reload_status( comp = comp ):
        self._result_WSURL = process_WSURL( self._status_WSURL )
        comp.becomes( comp, model = 'CHECKED' )

    u = ajax.Update(
        lambda r, comp = comp: comp.render( r ),
        reload_status
    )

    with h.div( class_ ='checker checked' ):
        h << component.Component( 
            ResultWSURL( self._status_WSURL, self._result_WSURL ),
            model = 'COLORED_LIGHT'
        )

    h << h.script( 
'''
function reload_status() {''' +
'''
{ACTION} ;'''.format( ACTION = u.generate_action( 2, h ) ) +
'''
} 
setTimeout("reload_status()",5000) ;
'''
    )

    return h.root

# ---------------------------------------------------------------

class WSGIApp( wsgi.WSGIApp ):

    def set_config( self, config_filename, config, error ):
        """Read the configuration parameters
        In:
            - ``config_filename`` -- the path to the configuration file
            - ``config`` -- the ``ConfigObj`` object, created from the configuration file
            - ``error`` -- the function to call in case of configuration errors
        """

        super(  WSGIApp, self ).set_config( config_filename, config, error )

        try:
            # Test de la presence du repertoire de configurations specifiques
            os.path.isdir( config[ 'specific' ][ 'path' ] )
        except:
            print 'no [specific]/path in %s' % ( config_filename )

def create_root_component( *args, **kwargs ):
    return component.Component( Cloudmgrnuiws() )

app = WSGIApp( create_root_component )
