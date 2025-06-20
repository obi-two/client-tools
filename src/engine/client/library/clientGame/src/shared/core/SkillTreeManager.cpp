//======================================================================
//
// SkillTreeManager.cpp
// A minimal manager for the classic pre-NGE skill tree system.
// It parses the skill_template datatable to determine which skills
// belong to each profession template.
//
//======================================================================

#include "clientGame/FirstClientGame.h"
#include "clientGame/SkillTreeManager.h"

#include "sharedFoundation/Crc.h"
#include "sharedUtility/DataTable.h"
#include "sharedUtility/DataTableManager.h"

#include <map>

//----------------------------------------------------------------------
namespace SkillTreeManagerNamespace
{
    SkillTreeManager::TemplateMap ms_templates;
    bool ms_installed = false;
}
using namespace SkillTreeManagerNamespace;

//----------------------------------------------------------------------
void SkillTreeManager::install()
{
    if (ms_installed)
        return;

    loadTemplateDatatable();
    ms_installed = true;
}

//----------------------------------------------------------------------
void SkillTreeManager::remove()
{
    ms_templates.clear();
    ms_installed = false;
}

//----------------------------------------------------------------------
bool SkillTreeManager::isInstalled()
{
    return ms_installed;
}

//----------------------------------------------------------------------
SkillTreeManager::SkillVector const &SkillTreeManager::getSkillsForTemplate(std::string const &templateName)
{
    static SkillVector emptyVector;
    TemplateMap::const_iterator i = ms_templates.find(Crc::normalizeAndCalculate(templateName.c_str()));
    if (i != ms_templates.end())
        return i->second.skills;

    return emptyVector;
}

//----------------------------------------------------------------------
void SkillTreeManager::loadTemplateDatatable()
{
    // This datatable is shared with the RoadmapManager and lists the
    // skill boxes associated with each profession template.
    DataTable *datatable = DataTableManager::getTable("datatables/skill_template/skill_template.iff", true);
    if (!datatable)
        return;

    unsigned int const numRows = static_cast<unsigned int>(datatable->getNumRows());
    int const templateNameColumn = datatable->findColumnNumber("templateName");
    int const templateColumn = datatable->findColumnNumber("template");

    for (unsigned int r = 0; r < numRows; ++r)
    {
        std::string const & templateName = datatable->getStringValue(templateNameColumn, r);
        std::string const & templateList = datatable->getStringValue(templateColumn, r);

        TemplateRecord rec;

        // Parse the comma separated skill list
        std::string::size_type curPos = 0;
        while (curPos != std::string::npos)
        {
            std::string::size_type nextPos = templateList.find(',', curPos);
            std::string skillName = templateList.substr(curPos, nextPos - curPos);
            if (!skillName.empty())
                rec.skills.push_back(skillName);
            curPos = nextPos;
            if (curPos != std::string::npos)
                ++curPos;
        }

        ms_templates.insert(std::make_pair(Crc::normalizeAndCalculate(templateName.c_str()), rec));
    }
}

//======================================================================
