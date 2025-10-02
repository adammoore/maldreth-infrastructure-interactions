# Glossary Content Management Guide

This guide explains how to update FAQ, terminology, and definitions in the PRISM glossary without modifying code.

---

## Quick Reference

| What to Update | File to Edit | Restart Needed? |
|----------------|--------------|-----------------|
| FAQ Questions/Answers | `config/glossary_content.py` | Yes |
| MaLDReTH Terminology | `config/glossary_content.py` | Yes |
| Interaction Type Definitions | `streamlined_app.py` | Yes |
| Lifecycle Stage Definitions | `streamlined_app.py` | Yes |

---

## Updating FAQ

### File: `config/glossary_content.py`

### Step 1: Edit FAQ_ITEMS List

```python
FAQ_ITEMS = [
    {
        'id': 'faq1',  # Unique ID for this question
        'question': 'Your question here?',
        'answer': '''Your answer here. Can include <strong>HTML</strong> formatting.''',
        'expanded': True  # Show by default (True) or collapsed (False)
    },
    # Add more FAQs...
]
```

### Step 2: Save and Restart Flask

```bash
# Stop Flask (Ctrl+C)
# Restart:
python3 streamlined_app.py
```

### Examples

#### Adding a New FAQ:

```python
{
    'id': 'faq7',
    'question': 'How do I cite PRISM in my research?',
    'answer': '''Please cite PRISM as: [Your Citation Here].
                 For more information, visit the <a href="{{ url_for('about') }}">About page</a>.''',
    'expanded': False
}
```

#### Editing an Existing FAQ:

Just modify the 'question' or 'answer' text in place.

#### Removing an FAQ:

Delete the entire dictionary block for that FAQ item.

---

## Verifying MaLDReTH Definitions

### ⚠️ CRITICAL: These definitions need verification against official RDA sources

### Official Sources to Check:

1. **RDA MaLDReTH II Working Group**: https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii
2. **RDA Outputs**: Check for published deliverables
3. **Contact**: Reach out to MaLDReTH II co-chairs for official definitions

### Verification Process:

1. **Locate Official Definition**
   - Find in RDA documents, meeting notes, or presentations
   - Confirm with co-chairs if uncertain

2. **Update Definition in Code**

   For FAQ items - edit `config/glossary_content.py`:
   ```python
   MALDRETH_TERMINOLOGY = {
       'MaLDReTH': {
           'expansion': '<strong>M</strong>apping...',
           'definition': 'Official definition here',
           'source': 'RDA MaLDReTH II Working Group',
           'verification_status': 'VERIFIED',  # Change from NEEDS_VERIFICATION
           'verified_date': '2025-10-02',  # Today's date
           'verified_by': 'Your Name',  # Your name or role
           'source_url': 'https://...'  # Link to source if available
       }
   }
   ```

   For lifecycle stages - edit `streamlined_app.py` (lines 143-228):
   ```python
   LIFECYCLE_STAGE_DEFINITIONS = {
       'PLAN': {
           'definition': 'Updated official definition',
           'activities': ['Updated list'],
           'typical_tools': ['Updated list'],
           'duration': 'Updated duration',
           'outputs': ['Updated outputs']
       },
       # ...
   }
   ```

3. **Mark as Verified**
   - Change `verification_status` to `'VERIFIED'`
   - Add `verified_date`
   - Add `verified_by`
   - Add `source_url` if available

### Current Verification Status:

**NEEDS VERIFICATION**:
- [ ] MaLDReTH acronym expansion (currently: "Mapping the Landscape of Digital Research Tools Harmonised")
- [ ] Research Data Lifecycle (RDL) 12-stage model definition
- [ ] All 12 lifecycle stage names (CONCEPTUALISE, PLAN, FUND, COLLECT, PROCESS, ANALYSE, STORE, PUBLISH, PRESERVE, SHARE, ACCESS, TRANSFORM)
- [ ] Each lifecycle stage's description, activities, tools, outputs
- [ ] Interaction type definitions

**VERIFIED**:
- [x] PRISM acronym and definition
- [x] Tool-related terminology (Exemplar Tool, Tool Category, Tool Interaction)
- [x] GORC definition

---

## Updating Interaction Type Definitions

### File: `streamlined_app.py`

### Location: Lines 62-140 (INTERACTION_TYPE_DEFINITIONS)

### Structure:

```python
INTERACTION_TYPE_DEFINITIONS = {
    'API Integration': {
        'definition': 'Clear, concise definition',
        'example': 'Real-world example',
        'when_to_use': 'Guidance on when to select this type',
        'technical_indicators': ['List', 'of', 'keywords'],
        'common_protocols': ['HTTP/HTTPS', 'REST']  # or common_tools, common_formats, etc.
    },
    # ... other types
}
```

### To Update:

1. Edit the definition text
2. Update examples to reflect current tools/practices
3. Add/remove technical indicators as needed
4. Save file
5. Restart Flask application

---

## Updating Lifecycle Stage Definitions

### File: `streamlined_app.py`

### Location: Lines 143-228 (LIFECYCLE_STAGE_DEFINITIONS)

### Structure:

```python
LIFECYCLE_STAGE_DEFINITIONS = {
    'PLAN': {
        'definition': 'Official stage definition',
        'activities': ['List', 'of', 'activities'],
        'typical_tools': ['Tool1', 'Tool2'],
        'duration': 'Time estimate',
        'outputs': ['What', 'is', 'produced']
    },
    # ... other stages
}
```

### To Update:

1. Locate the stage you want to update
2. Modify any of the fields
3. Ensure consistency with RDA official documentation
4. Save file
5. Restart Flask application

---

## Testing Your Changes

### 1. Start Flask Application

```bash
cd /path/to/maldreth-infrastructure-interactions
source venv/bin/activate
python3 streamlined_app.py
```

### 2. Check for Errors

Look for these messages in the terminal:
- ✅ `Glossary config not found, using hardcoded values` - Config file not loaded (check path)
- ✅ No errors - Config loaded successfully

### 3. Test in Browser

Visit: http://localhost:5001/glossary

**Check**:
- [ ] FAQ section shows your changes
- [ ] New FAQs appear
- [ ] Accordion expand/collapse works
- [ ] HTML formatting displays correctly
- [ ] Links work
- [ ] No broken layouts

### 4. Verify No Regressions

Visit these pages to ensure nothing broke:
- http://localhost:5001/ (Homepage)
- http://localhost:5001/add-interaction (Form)
- http://localhost:5001/interactions (List)

---

## Common Tasks

### Add a Verification Note to an FAQ

```python
{
    'id': 'faq1',
    'question': 'What is the difference between "API Integration" and "Web Service"?',
    'answer': '''<strong>API Integration</strong> refers to modern RESTful or GraphQL APIs...

                 <div class="alert alert-info mt-2">
                     <small><strong>Note:</strong> This definition was verified against
                     RDA documentation on 2025-10-02.</small>
                 </div>''',
    'expanded': True
}
```

### Link to Another Page in FAQ Answer

```python
'answer': '''For more information, see the
             <a href="{{ url_for('about') }}">About page</a> or
             <a href="{{ url_for('information_structures') }}">Information Structures</a>.'''
```

### Add External Link

```python
'answer': '''Visit the
             <a href="https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii" target="_blank">
             MaLDReTH II Working Group</a> for more details.'''
```

---

## Troubleshooting

### FAQ Not Showing

**Problem**: My FAQ changes don't appear

**Solutions**:
1. Check Python syntax - any errors will prevent loading
2. Ensure Flask was restarted after changes
3. Check browser console for JavaScript errors
4. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)

### Import Error

**Problem**: `ImportError: cannot import name 'FAQ_ITEMS'`

**Solutions**:
1. Check file path: `config/glossary_content.py` exists
2. Check Python syntax in glossary_content.py
3. Ensure `__init__.py` doesn't exist in config/ (not a package)
4. Check variable name spelling exactly matches

### HTML Not Rendering

**Problem**: HTML tags show as text instead of formatting

**Solutions**:
1. Use triple quotes for multi-line strings: `'''...'''`
2. Ensure HTML is valid (close all tags)
3. Check for conflicting quotes (use `\'` for apostrophes inside strings)

---

## Best Practices

### ✅ DO:
- Verify definitions with official RDA sources before marking as verified
- Keep answers concise and scannable
- Use HTML formatting sparingly (bold, links, lists only)
- Test all changes locally before committing
- Add verification dates and sources
- Keep FAQ items focused on one question each

### ❌ DON'T:
- Don't include JavaScript in FAQ answers
- Don't use inline CSS (use Bootstrap classes instead)
- Don't make FAQ answers longer than 3-4 paragraphs
- Don't edit files directly on production server
- Don't mark as verified without official source confirmation

---

## Contact for Verification

### MaLDReTH II Co-Chairs:
- Contact via RDA MaLDReTH II Working Group
- Email: [To be added]
- RDA Page: https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii

### For Technical Issues:
- GitHub Issues: [Repository URL]
- Developer: [Contact info]

---

## Checklist: Before Deploying Changes

- [ ] All changes verified against official RDA sources
- [ ] Python syntax validated (`python3 -m py_compile config/glossary_content.py`)
- [ ] Tested locally - all FAQ items display correctly
- [ ] No broken links
- [ ] HTML formatting renders properly
- [ ] No console errors in browser DevTools
- [ ] Existing functionality still works (homepage, forms, etc.)
- [ ] Changes documented in git commit message
- [ ] Verification status updated appropriately

---

**Last Updated**: 2025-10-02
**Version**: 1.0
**Maintainer**: PRISM Development Team
