#include "ViewerLocalization.H"

#include "Localization.h"

#include <FL/Fl.H>
#include <FL/Fl_Group.H>
#include <FL/Fl_Menu_.H>
#include <FL/Fl_Window.H>

#include <cstring>

namespace
{

void TranslateMenu( Fl_Menu_ * menu )
{
    const Fl_Menu_Item * items = menu->menu();
    if ( !items )
    {
        return;
    }

    for ( int i = 0; i < menu->size(); ++i )
    {
        Fl_Menu_Item * item = const_cast< Fl_Menu_Item * >( &items[i] );
        if ( item->text )
        {
            const char * translated = vsp::l10n::Tr( item->text );
            if ( std::strcmp( translated, item->text ) != 0 )
            {
                item->label( translated );
            }
        }
    }
}

void TranslateWidget( Fl_Widget * widget )
{
    if ( !widget )
    {
        return;
    }

    if ( widget->label() && widget->label()[0] )
    {
        const char * translated = vsp::l10n::Tr( widget->label() );
        if ( std::strcmp( translated, widget->label() ) != 0 )
        {
            widget->copy_label( translated );
        }
    }

    Fl_Menu_ * menu = dynamic_cast< Fl_Menu_ * >( widget );
    if ( menu )
    {
        TranslateMenu( menu );
    }

    Fl_Group * group = dynamic_cast< Fl_Group * >( widget );
    if ( group )
    {
        for ( int i = 0; i < group->children(); ++i )
        {
            TranslateWidget( group->child( i ) );
        }
    }
}

int LocalizationHandler( int )
{
    for ( Fl_Window * window = Fl::first_window(); window; window = Fl::next_window( window ) )
    {
        TranslateWidget( window );
    }
    return 0;
}

void TranslateOpenWindows( void * )
{
    LocalizationHandler( 0 );
}

}

void InstallViewerLocalization()
{
    vsp::l10n::LoadTranslations();
    Fl::add_handler( LocalizationHandler );
    Fl::add_timeout( 0.0, TranslateOpenWindows );
}
