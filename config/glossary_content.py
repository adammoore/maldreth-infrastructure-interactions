"""
Glossary Content Configuration
Editable definitions and FAQ for PRISM Glossary

This file contains all glossary content that may need updates.
Edit this file to update definitions, examples, or FAQ without touching templates.

VERIFICATION STATUS:
- Lifecycle stage definitions: NEEDS VERIFICATION against RDA MaLDReTH II outputs
- Official source: https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii
"""

# FAQ Items - Easy to add/edit/remove
FAQ_ITEMS = [
    {
        'id': 'faq1',
        'question': 'What is the difference between "API Integration" and "Web Service"?',
        'answer': '''<strong>API Integration</strong> refers to modern RESTful or GraphQL APIs with programmatic access,
                     typically using JSON. <strong>Web Service</strong> is broader and includes older protocols like
                     SOAP, XML-RPC, or domain-specific protocols like OAI-PMH. If in doubt, "API Integration" is
                     usually the better choice for contemporary tools.''',
        'expanded': True  # Show this one by default
    },
    {
        'id': 'faq2',
        'question': 'Can one interaction belong to multiple lifecycle stages?',
        'answer': '''Currently, each interaction is assigned to one primary lifecycle stage. If an interaction
                     genuinely supports multiple stages, choose the stage where it's most commonly used, and mention
                     the other stages in the description or examples field.''',
        'expanded': False
    },
    {
        'id': 'faq3',
        'question': 'What if the tools I want to add aren\'t in PRISM yet?',
        'answer': '''When you add an interaction via CSV upload, PRISM will automatically create any missing tools.
                     For manual entry through the web form, please contact the MaLDReTH II working group to request
                     tool additions, or use the CSV bulk upload feature.''',
        'expanded': False
    },
    {
        'id': 'faq4',
        'question': 'How is PRISM different from other tool catalogs?',
        'answer': '''PRISM focuses specifically on <strong>interactions between tools</strong> rather than just
                     cataloging individual tools. While many catalogs list research tools, PRISM maps how they
                     connect, integrate, and work together across the research data lifecycle. This makes it
                     uniquely valuable for understanding research infrastructure interoperability.''',
        'expanded': False
    },
    {
        'id': 'faq5',
        'question': 'Can I edit or update an interaction I submitted?',
        'answer': '''Yes! Every interaction has an "Edit" button on its detail page. You can update any field
                     to improve accuracy or add additional information. All edits help improve the quality of
                     PRISM's knowledge base.''',
        'expanded': False
    },
    {
        'id': 'faq6',
        'question': 'Who maintains PRISM and how can I get involved?',
        'answer': '''PRISM is maintained by the <a href="https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii" target="_blank">
                     MaLDReTH II RDA Working Group</a>. You can get involved by:
                     <ul class="mt-2">
                         <li>Contributing interaction data through PRISM</li>
                         <li>Joining the MaLDReTH II working group</li>
                         <li>Participating in RDA plenary sessions</li>
                         <li>Providing feedback and suggestions</li>
                     </ul>''',
        'expanded': False
    }
]

# Instructions for updating FAQ
FAQ_UPDATE_INSTRUCTIONS = """
TO ADD A NEW FAQ:
1. Add a new dictionary to FAQ_ITEMS list with:
   - 'id': unique identifier (e.g., 'faq7')
   - 'question': The question text
   - 'answer': The answer (can include HTML)
   - 'expanded': True (show by default) or False (collapsed)

2. Restart Flask application

EXAMPLE:
{
    'id': 'faq7',
    'question': 'How do I cite PRISM?',
    'answer': 'Please cite PRISM as: [Citation text here]',
    'expanded': False
}
"""

# MaLDReTH Terminology Definitions
# NOTE: These should be verified against official RDA MaLDReTH II outputs
MALDRETH_TERMINOLOGY = {
    'MaLDReTH': {
        'expansion': '<strong>M</strong>apping the <strong>L</strong>andscape of <strong>D</strong>igital <strong>Re</strong>search <strong>T</strong>ools <strong>H</strong>armonised',
        'definition': '''The harmonised Research Data Lifecycle (RDL) model created by the RDA-OfR Working Group
                        to serve as the foundational framework for categorising and characterising various types of
                        digital research tools. It provides a common language and reference point for researchers,
                        data stewards, and tool developers, facilitating collaboration and interoperability within the
                        research data ecosystem.''',
        'source': 'RDA-OfR Mapping the Landscape of Digital Research Tools WG Deliverable 1',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02',
        'verified_by': 'PRISM Development Team',
        'source_url': 'https://www.rd-alliance.org/wp-content/uploads/2024/09/D1_The-creation-of-a-harmonised-research-data-lifecycle-RDL-model-and-crosswalk-to-existing-models-.pdf'
    },
    'PRISM': {
        'expansion': '<strong>P</strong>latform for <strong>R</strong>esearch <strong>I</strong>nfrastructure <strong>S</strong>ynergy <strong>M</strong>apping',
        'definition': '''This web application - a key output of the MaLDReTH II initiative.''',
        'source': 'PRISM Development Team',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02'
    },
    'Exemplar Tool': {
        'definition': '''A representative tool within a category, demonstrating typical characteristics
                        and capabilities.''',
        'dynamic_context': 'Currently PRISM contains {total_tools} exemplar tools.',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02'
    },
    'Tool Category': {
        'definition': '''A classification group for similar tools within a lifecycle stage. Categories help
                        organize tools by function and purpose.''',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02'
    },
    'Tool Interaction': {
        'definition': '''A connection or integration between two research tools, describing how they
                        communicate or work together.''',
        'dynamic_context': 'PRISM currently contains {total_interactions} documented interactions.',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02'
    },
    'Research Data Lifecycle (RDL)': {
        'definition': '''The complete journey of research data from initial concept through to reuse and transformation,
                        represented in the MaLDReTH model as 12 distinct stages: CONCEPTUALISE, PLAN, FUND, COLLECT,
                        PROCESS, ANALYSE, STORE, PUBLISH, PRESERVE, SHARE, ACCESS, and TRANSFORM. Created through
                        harmonisation of 5 existing RDL models using semantic distance methodology.''',
        'source': 'RDA-OfR Mapping the Landscape of Digital Research Tools WG Deliverable 1',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02',
        'verified_by': 'PRISM Development Team',
        'source_url': 'https://www.rd-alliance.org/wp-content/uploads/2024/09/D1_The-creation-of-a-harmonised-research-data-lifecycle-RDL-model-and-crosswalk-to-existing-models-.pdf'
    },
    'GORC': {
        'expansion': '<strong>G</strong>lobal <strong>O</strong>pen <strong>R</strong>esearch <strong>C</strong>ommons',
        'definition': '''An RDA initiative that PRISM contributes to, focused on
                        improving interoperability and FAIR data practices.''',
        'source': 'Research Data Alliance',
        'verification_status': 'VERIFIED',
        'verified_date': '2025-10-02'
    }
}

# Verification checklist
VERIFICATION_CHECKLIST = """
CONTENT VERIFICATION CHECKLIST:
================================

HIGH PRIORITY - Needs Verification:
- [ ] MaLDReTH acronym expansion
- [ ] Research Data Lifecycle 12-stage model definition
- [ ] Lifecycle stage names (CONCEPTUALISE, PLAN, FUND, etc.)
- [ ] Lifecycle stage descriptions in streamlined_app.py

MEDIUM PRIORITY - Should Review:
- [ ] Interaction type definitions
- [ ] Technical indicators for each interaction type
- [ ] Common protocols/tools lists

VERIFIED:
- [x] PRISM acronym and definition
- [x] Tool-related terminology (Exemplar Tool, Tool Category, Tool Interaction)
- [x] GORC definition

OFFICIAL SOURCES TO CHECK:
1. RDA MaLDReTH II Working Group page: https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii
2. RDA outputs/deliverables: Check for published documents
3. Meeting notes and presentations from MaLDReTH II sessions
4. Contact co-chairs for official definitions if not publicly available

TO MARK AS VERIFIED:
1. Confirm definition matches official source
2. Update 'verification_status' to 'VERIFIED'
3. Add 'verified_date' (YYYY-MM-DD)
4. Add 'verified_by' field with name/role
5. Add 'source_url' if available
"""
