#ifndef INCLUDED_SkillTreeManager_H
#define INCLUDED_SkillTreeManager_H

#include <string>
#include <vector>

class SkillObject;

class SkillTreeManager
{
public:
    typedef std::vector<std::string> SkillVector;

    static void install();
    static void remove();

    static bool isInstalled();

    // Returns the list of skills that belong to the given template.
    static SkillVector const &getSkillsForTemplate(std::string const &templateName);

private:
    SkillTreeManager();
    ~SkillTreeManager();

    static void loadTemplateDatatable();

    struct TemplateRecord
    {
        SkillVector skills;
    };

    typedef std::map<uint32, TemplateRecord> TemplateMap;
    static TemplateMap ms_templates;
    static bool ms_installed;
};

#endif
