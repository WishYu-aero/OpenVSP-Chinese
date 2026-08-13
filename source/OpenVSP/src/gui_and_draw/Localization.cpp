//
// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.
//

#include "Localization.h"

#include <algorithm>
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <map>
#include <mutex>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#endif

namespace
{

std::once_flag g_LoadOnce;
std::map< std::string, std::string > g_Translations;
std::map< std::string, std::string > g_FoldedTranslations;

std::string Trim( const std::string & text )
{
    const std::string ws = " \t\r\n";
    const size_t start = text.find_first_not_of( ws );
    if ( start == std::string::npos )
    {
        return std::string();
    }

    const size_t end = text.find_last_not_of( ws );
    return text.substr( start, end - start + 1 );
}

std::string FoldAscii( const std::string & text )
{
    std::string folded = text;
    std::transform( folded.begin(), folded.end(), folded.begin(), []( unsigned char ch )
    {
        return ch >= 'A' && ch <= 'Z' ? static_cast< char >( ch - 'A' + 'a' ) : static_cast< char >( ch );
    } );
    return folded;
}

bool IsHexDigit( char ch )
{
    return ( ch >= '0' && ch <= '9' ) ||
           ( ch >= 'a' && ch <= 'f' ) ||
           ( ch >= 'A' && ch <= 'F' );
}

int HexValue( char ch )
{
    if ( ch >= '0' && ch <= '9' )
    {
        return ch - '0';
    }
    if ( ch >= 'a' && ch <= 'f' )
    {
        return ch - 'a' + 10;
    }
    return ch - 'A' + 10;
}

void AppendUtf8( std::string & out, unsigned int codepoint )
{
    if ( codepoint <= 0x7F )
    {
        out.push_back( static_cast< char >( codepoint ) );
    }
    else if ( codepoint <= 0x7FF )
    {
        out.push_back( static_cast< char >( 0xC0 | ( codepoint >> 6 ) ) );
        out.push_back( static_cast< char >( 0x80 | ( codepoint & 0x3F ) ) );
    }
    else
    {
        out.push_back( static_cast< char >( 0xE0 | ( codepoint >> 12 ) ) );
        out.push_back( static_cast< char >( 0x80 | ( ( codepoint >> 6 ) & 0x3F ) ) );
        out.push_back( static_cast< char >( 0x80 | ( codepoint & 0x3F ) ) );
    }
}

bool ParseJsonString( const std::string & text, size_t & pos, std::string & out )
{
    if ( pos >= text.size() || text[pos] != '"' )
    {
        return false;
    }

    pos++;
    out.clear();
    while ( pos < text.size() )
    {
        char ch = text[pos++];
        if ( ch == '"' )
        {
            return true;
        }
        if ( ch != '\\' )
        {
            out.push_back( ch );
            continue;
        }

        if ( pos >= text.size() )
        {
            return false;
        }

        char esc = text[pos++];
        switch ( esc )
        {
            case '"': out.push_back( '"' ); break;
            case '\\': out.push_back( '\\' ); break;
            case '/': out.push_back( '/' ); break;
            case 'b': out.push_back( '\b' ); break;
            case 'f': out.push_back( '\f' ); break;
            case 'n': out.push_back( '\n' ); break;
            case 'r': out.push_back( '\r' ); break;
            case 't': out.push_back( '\t' ); break;
            case 'u':
            {
                if ( pos + 4 > text.size() ||
                     !IsHexDigit( text[pos] ) ||
                     !IsHexDigit( text[pos + 1] ) ||
                     !IsHexDigit( text[pos + 2] ) ||
                     !IsHexDigit( text[pos + 3] ) )
                {
                    return false;
                }

                unsigned int cp = 0;
                for ( int i = 0; i < 4; i++ )
                {
                    cp = ( cp << 4 ) + HexValue( text[pos + i] );
                }
                pos += 4;
                AppendUtf8( out, cp );
                break;
            }
            default:
                out.push_back( esc );
                break;
        }
    }

    return false;
}

bool LoadJsonObject( const std::string & text )
{
    size_t pos = 0;
    while ( pos < text.size() && text[pos] != '{' )
    {
        pos++;
    }
    if ( pos >= text.size() )
    {
        return false;
    }
    pos++;

    while ( pos < text.size() )
    {
        while ( pos < text.size() && std::string( " \t\r\n," ).find( text[pos] ) != std::string::npos )
        {
            pos++;
        }
        if ( pos >= text.size() || text[pos] == '}' )
        {
            return true;
        }

        std::string key;
        std::string val;
        if ( !ParseJsonString( text, pos, key ) )
        {
            return false;
        }

        while ( pos < text.size() && std::string( " \t\r\n" ).find( text[pos] ) != std::string::npos )
        {
            pos++;
        }
        if ( pos >= text.size() || text[pos] != ':' )
        {
            return false;
        }
        pos++;
        while ( pos < text.size() && std::string( " \t\r\n" ).find( text[pos] ) != std::string::npos )
        {
            pos++;
        }
        if ( !ParseJsonString( text, pos, val ) )
        {
            return false;
        }

        if ( !key.empty() && !val.empty() )
        {
            g_Translations[key] = val;
            g_FoldedTranslations[FoldAscii( key )] = val;
        }
    }

    return true;
}

void TryLoadFile( const std::string & path )
{
    if ( path.empty() )
    {
        return;
    }

    std::ifstream in( path.c_str(), std::ios::binary );
    if ( !in )
    {
        return;
    }

    std::string text( ( std::istreambuf_iterator< char >( in ) ), std::istreambuf_iterator< char >() );
    LoadJsonObject( text );
}

#ifdef _WIN32
void TryLoadFile( const std::wstring & path )
{
    if ( path.empty() )
    {
        return;
    }

    FILE * file = _wfopen( path.c_str(), L"rb" );
    if ( !file )
    {
        return;
    }

    std::string text;
    char buffer[4096];
    size_t count = 0;
    while ( ( count = fread( buffer, 1, sizeof( buffer ), file ) ) > 0 )
    {
        text.append( buffer, count );
    }
    fclose( file );
    LoadJsonObject( text );
}
#endif

#ifdef _WIN32
std::wstring ExeDir()
{
    std::vector< wchar_t > path( MAX_PATH );
    for ( ;; )
    {
        DWORD len = GetModuleFileNameW( nullptr, path.data(), static_cast< DWORD >( path.size() ) );
        if ( len == 0 )
        {
            break;
        }
        if ( len < path.size() - 1 )
        {
            std::wstring exe( path.data(), len );
            size_t pos = exe.find_last_of( L"\\/" );
            return pos == std::wstring::npos ? std::wstring( L"." ) : exe.substr( 0, pos );
        }
        path.resize( path.size() * 2 );
    }
    return std::wstring( L"." );
}
#endif

void LoadDefaultTranslations()
{
    const char * env = std::getenv( "OPENVSP_TRANSLATIONS" );
    if ( env )
    {
        TryLoadFile( env );
    }

#ifdef _WIN32
    const std::wstring exe_dir = ExeDir();
    TryLoadFile( exe_dir + L"\\translations\\zh-CN.json" );
    TryLoadFile( exe_dir + L"\\zh-CN.json" );
#else
    TryLoadFile( "./translations/zh-CN.json" );
    TryLoadFile( "./zh-CN.json" );
#endif
}

}

namespace vsp
{
namespace l10n
{

void LoadTranslations()
{
    std::call_once( g_LoadOnce, LoadDefaultTranslations );
}

bool IsEnabled()
{
    LoadTranslations();
    return !g_Translations.empty();
}

std::string Tr( const std::string & text )
{
    LoadTranslations();

    const auto exact_iter = g_Translations.find( text );
    if ( exact_iter != g_Translations.end() )
    {
        return exact_iter->second;
    }

    const std::string key = Trim( text );
    if ( key.empty() )
    {
        return text;
    }

    const auto iter = g_Translations.find( key );
    if ( iter != g_Translations.end() )
    {
        return iter->second;
    }

    const auto folded_iter = g_FoldedTranslations.find( FoldAscii( key ) );
    if ( folded_iter != g_FoldedTranslations.end() )
    {
        return folded_iter->second;
    }

    return text;
}

const char * Tr( const char * text )
{
    if ( !text )
    {
        return text;
    }

    LoadTranslations();

    const auto exact_iter = g_Translations.find( text );
    if ( exact_iter != g_Translations.end() )
    {
        return exact_iter->second.c_str();
    }

    const std::string key = Trim( text );
    const auto iter = g_Translations.find( key );
    if ( iter != g_Translations.end() )
    {
        // The translation table is immutable after LoadTranslations(), so this
        // pointer remains valid and multiple Tr() arguments cannot alias.
        return iter->second.c_str();
    }


    const auto folded_iter = g_FoldedTranslations.find( FoldAscii( key ) );
    if ( folded_iter != g_FoldedTranslations.end() )
    {
        return folded_iter->second.c_str();
    }

    return text;
}

std::string TrMenuPath( const std::string & path )
{
    std::string translated;
    size_t start = 0;
    while ( start <= path.size() )
    {
        const size_t slash = path.find( '/', start );
        const std::string part = path.substr( start, slash == std::string::npos ? std::string::npos : slash - start );
        if ( !translated.empty() )
        {
            translated += "/";
        }
        translated += Tr( part );

        if ( slash == std::string::npos )
        {
            break;
        }
        start = slash + 1;
    }

    return translated;
}

std::string TrBrowserHeader( const std::string & header )
{
    std::string translated;
    size_t start = 0;
    while ( start < header.size() )
    {
        const size_t styled_marker = header.find( "@b@.", start );
        const size_t centered_marker = header.find( "@b@c@.", start );
        size_t label_start = std::string::npos;
        if ( centered_marker != std::string::npos )
        {
            label_start = centered_marker + 6;
        }
        else if ( styled_marker != std::string::npos )
        {
            label_start = styled_marker + 4;
        }
        if ( label_start == std::string::npos )
        {
            translated += header.substr( start );
            break;
        }

        translated += header.substr( start, label_start - start );
        const size_t end = header.find_first_of( ":|", label_start );
        translated += Tr( header.substr( label_start, end - label_start ) );
        if ( end == std::string::npos )
        {
            break;
        }
        translated += header[end];
        start = end + 1;
    }
    return translated;
}

}
}
