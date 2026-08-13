//
// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.
//

#if !defined(LOCALIZATION__INCLUDED_)
#define LOCALIZATION__INCLUDED_

#include <string>

namespace vsp
{
namespace l10n
{

std::string Tr( const std::string & text );
const char * Tr( const char * text );
std::string TrMenuPath( const std::string & path );
std::string TrBrowserHeader( const std::string & header );

void LoadTranslations();
bool IsEnabled();

}
}

#endif // !defined(LOCALIZATION__INCLUDED_)
