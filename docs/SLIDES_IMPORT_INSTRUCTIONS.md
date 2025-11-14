# How to Import Slides into Google Slides

## Method 1: Direct Import (Recommended)

1. **Open the HTML file** in your browser:
   ```
   /Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/docs/RDA_IDW_PRESENTATION_IMPORT.html
   ```

2. **Print to PDF**:
   - Press `Cmd + P` (Mac) or `Ctrl + P` (Windows)
   - Select "Save as PDF" as the destination
   - Adjust settings:
     - Paper size: Letter or A4
     - Margins: None
     - Background graphics: ✓ Checked
   - Save as `RDA_IDW_Presentation.pdf`

3. **Import to Google Slides**:
   - Go to https://slides.google.com
   - Click "Blank" to create new presentation
   - Go to **File > Import slides**
   - Upload the PDF file
   - Select "All" slides
   - **Uncheck** "Keep original theme"
   - Click "Import slides"

4. **Apply Google Slides theme**:
   - Select all slides (Cmd/Ctrl + A)
   - Go to **Slide > Apply layout**
   - Choose "Title and body" or your preferred layout
   - Apply RDA or institutional theme if available

## Method 2: Manual Recreation (Better Control)

### Recommended Theme
- Use "Simple Light" or "Modern Writer" Google Slides theme
- Primary color: #1a73e8 (Google Blue) or RDA brand color
- Font: Roboto or Arial

### Slide-by-Slide Guide

**Slide 1: Title**
- Layout: Title slide
- Title: MaLDReTH II
- Subtitle: Mapping the Research Infrastructure Landscape
- Add your name, affiliation, date

**Slides 2-22: Content**
- Layout: Title and body
- Copy headers from HTML
- Copy bullet points
- Add boxes using "Shapes" (rounded rectangle)
- Color boxes with light blue (#e8f0fe) or yellow (#fff3cd)

**For diagrams (Slides 5, 7, 19):**
- Insert as "Text box" with monospace font (Courier New)
- Or create using Google Drawing
- Alternatively, screenshot the HTML version

### Tips for Quick Import
1. Copy/paste content directly from the HTML (open in browser, select text)
2. Use keyboard shortcuts:
   - `Cmd/Ctrl + D` = Duplicate slide
   - `Cmd/Ctrl + M` = New slide
   - `Cmd/Ctrl + Shift + C/V` = Copy/paste formatting
3. Create master slides for repeated layouts (boxes, headers)
4. Use "Format painter" for consistent styling

## Method 3: Use Presentation Software

### PowerPoint
1. Open PowerPoint
2. Import the HTML or paste content
3. Export as .pptx
4. Upload to Google Drive
5. Right-click > "Open with Google Slides"

### Keynote (Mac)
1. Open Keynote
2. Create new presentation
3. Paste content from HTML
4. Export as PowerPoint (.pptx)
5. Import to Google Slides

## Customization Checklist

Before your presentation:

- [ ] Add your name and affiliation (Slide 1)
- [ ] Insert PRISM live URL (Slides 1, 9, 21)
- [ ] Add QR code to Slide 1 (use qr-code-generator.com)
- [ ] Insert session number and date (Slide 1)
- [ ] Create feedback survey and add link (Slide 16)
- [ ] Update "Initial Findings" template (Slide 17) for live note-taking
- [ ] Add institution logo if required
- [ ] Test all visualizations work in your PRISM instance
- [ ] Screenshot PRISM features for Slide 9 if needed
- [ ] Review slide notes for presenter guidance
- [ ] Add backup slides if needed (technical details, FAQ)

## Presentation Tips

1. **Slide 9 (Live Demo):**
   - Have PRISM open in another tab
   - Test all features beforehand
   - Have backup screenshots in case of connectivity issues

2. **Slides 11-15 (User Testing):**
   - Display one task at a time
   - Give users time to complete
   - Have note-takers record observations

3. **Slide 16 (Feedback):**
   - Create Google Form with questions from the slide
   - Share link via QR code or chat
   - Monitor responses in real-time

4. **Slide 17 (Findings):**
   - Designate someone to type notes live
   - Or use sticky notes on a whiteboard
   - Display themes as they emerge

## Additional Resources

- **Original markdown:** `RDA_IDW_PRESENTATION.md` (30 detailed slides)
- **HTML version:** `RDA_IDW_PRESENTATION_IMPORT.html` (22 core slides)
- **Facilitator notes:** See markdown version for expanded content

## File Locations

All files are in:
```
/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/docs/
├── RDA_IDW_PRESENTATION.md                  (Full 30-slide deck with notes)
├── RDA_IDW_PRESENTATION_IMPORT.html         (22-slide HTML for import)
└── SLIDES_IMPORT_INSTRUCTIONS.md            (This file)
```

## Support

If you need help:
1. See the detailed markdown version for full speaker notes
2. Contact: maldreth-wg@rd-alliance.org
3. Backup plan: Present from the HTML file directly in browser (full-screen mode)
