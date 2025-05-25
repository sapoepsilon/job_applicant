#!/usr/bin/env python3
"""
Markdown to PDF Converter

This module handles conversion of Markdown files to PDF format with specific
formatting requirements for resumes (no bullet indentation, clean layout).

Converts markdown to HTML first, then uses available tools to generate PDF.
The module is completely LaTeX-agnostic and doesn't depend on wkhtmltopdf.

Note: PDF generation requires external tools. Consider using weasyprint or
other HTML-to-PDF converters as alternatives.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional



class MarkdownToPDFConverter:
    """Convert Markdown files to PDF with custom formatting."""
    
    def __init__(self):
        """Initialize the converter."""
        self.pandoc_available = shutil.which('pandoc') is not None
        self.weasyprint_available = self._check_weasyprint()
    
    def _check_weasyprint(self) -> bool:
        """Check if weasyprint is available."""
        try:
            import weasyprint
            return True
        except ImportError:
            return False
    
    def preprocess_markdown(self, markdown_file: Path) -> Path:
        """Preprocess markdown to ensure no bullet indentation.
        
        Args:
            markdown_file: Path to the markdown file
            
        Returns:
            Path to the preprocessed temporary markdown file
        """
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a temporary file with processed content
        temp_file = markdown_file.with_suffix('.temp.md')
        
        # Process the content to ensure no indentation
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Remove any leading whitespace from bullet points
            if line.strip().startswith('-'):
                # Keep only the dash and content, no leading spaces
                processed_lines.append('- ' + line.strip()[1:].strip())
            else:
                processed_lines.append(line)
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(processed_lines))
        
        return temp_file
    
    def markdown_to_html(self, markdown_file: Path) -> str:
        """Convert markdown to HTML with styling for PDF conversion.
        
        Args:
            markdown_file: Path to the markdown file
            
        Returns:
            HTML content as string
        """
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Basic HTML template with styling
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        /* SPACING CONTROL GUIDE:
         * - h1 margins: control space around name (top/bottom)
         * - h2 margins: control space around section headers (EXPERIENCE, EDUCATION, etc.)
         * - h3 margins: control space around job titles
         * - p margins: control space between contact info and skills
         * - ul margins: control space around bullet point lists
         * - Empty lines: controlled in _markdown_to_html_content() method
         */
        body {{
            font-family: Arial, sans-serif;
            font-size: 9pt;
            line-height: 1.4;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        h1 {{
            font-size: 20pt;
            margin: -5px 0 5px 0;  /* top right bottom left - reduced top margin from 10px to 5px */
            text-align: center;
        }}
        h2 {{
            font-size: 14pt;
            margin: 5px 0 5px 0;  /* MAIN SPACING CONTROL: reduced top margin from 15px to 10px */
            border-bottom: 1px solid #333;
            padding-bottom: 2px;   /* slight padding for the underline */
        }}
        h3 {{
            font-size: 12pt;
            margin: 5px 0 3px 0;   /* small spacing for job titles */
        }}
        p {{
            margin: 2px 0;         /* minimal spacing for paragraphs */
            text-align: left;
        }}
        ul {{
            margin: 3px 0 5px 0;   /* small top margin, slightly larger bottom */
            padding-left: 0;
            list-style-type: none;
        }}
        li {{
            margin: 3px 0;
            padding-left: 0;
        }}
        li:before {{
            content: "- ";
            margin-right: 5px;
        }}
        em {{
            color: #666;
        }}
        a {{
            color: #0066cc;
            text-decoration: underline;  /* Make links clearly visible */
        }}
        a:hover {{
            color: #0052a3;
            text-decoration: underline;
        }}
        strong {{
            font-weight: 600;
        }}
    </style>
</head>
<body>
{self._markdown_to_html_content(markdown_content)}
</body>
</html>"""
        
        return html_template
    
    def _markdown_to_html_content(self, markdown_content: str) -> str:
        """Convert markdown content to HTML.
        
        Args:
            markdown_content: Markdown content as string
            
        Returns:
            HTML content as string
        """
        # Convert headers
        lines = markdown_content.split('\n')
        html_lines = []
        
        for line in lines:
            # Headers
            if line.startswith('### '):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith('## '):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('# '):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            # Bullet points
            elif line.startswith('- '):
                if not html_lines or not html_lines[-1].endswith('</ul>'):
                    html_lines.append('<ul>')
                html_lines.append(f"<li>{self._process_inline_markdown(line[2:])}</li>")
                # Check if next line is not a bullet
                if lines.index(line) == len(lines) - 1 or not lines[lines.index(line) + 1].startswith('- '):
                    html_lines.append('</ul>')
            # Bold text lines (for skills)
            elif line.startswith('**') and ':' in line:
                html_lines.append(f"<p>{self._process_inline_markdown(line)}</p>")
            # Regular paragraphs
            elif line.strip():
                html_lines.append(f"<p>{self._process_inline_markdown(line)}</p>")
            else:
                # SPACING CONTROL: Empty lines become <br> tags
                # Comment out the line below to remove extra spacing between sections
                # html_lines.append('<br>')
                pass  # Currently skipping empty lines to reduce spacing
        
        return '\n'.join(html_lines)
    
    def _process_inline_markdown(self, text: str) -> str:
        """Process inline markdown elements like bold, italic, and links.
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            HTML formatted text
        """
        import re
        
        # Process links [text](url) - converts to clickable hyperlinks in PDF
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Process raw URLs (optional - comment out if you want raw URLs to stay visible)
        # This will hide raw URLs and show just the domain name
        # text = re.sub(r'https?://([^\s]+)', r'<a href="https://\1">\1</a>', text)
        
        # Process bold **text**
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        
        # Process italic *text*
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        
        # Process bullet character
        text = text.replace('•', '&bull;')
        
        return text
    
    def convert_with_pandoc(self, output_pdf: Path, 
                           temp_markdown: Path) -> bool:
        """Convert markdown to PDF using pandoc.
        
        Args:
            output_pdf: Output PDF file path
            temp_markdown: Preprocessed markdown file path
            
        Returns:
            True if conversion successful, False otherwise
        """
        if not self.pandoc_available:
            return False
            
        try:
            # Use pandoc with HTML intermediate conversion
            # First convert markdown to HTML, then HTML to PDF
            temp_html = output_pdf.with_suffix('.temp.html')
            
            # Convert markdown to HTML
            html_content = self.markdown_to_html(temp_markdown)
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Convert HTML to PDF using pandoc's built-in converter
            result = subprocess.run([
                'pandoc',
                str(temp_html),
                '-o', str(output_pdf),
                '-f', 'html',
                '-t', 'pdf',
                '--metadata', 'title=Resume'
            ], capture_output=True, text=True, timeout=30)
            
            # Clean up temp file
            if temp_html.exists():
                temp_html.unlink()
            
            if result.returncode == 0 and output_pdf.exists():
                return True
            else:
                print(f"Pandoc error: {result.stderr}")
                # Try with HTML intermediate as fallback
                try:
                    # Convert to HTML first
                    html_content = self.markdown_to_html(temp_markdown)
                    temp_html = output_pdf.with_suffix('.temp.html')
                    
                    with open(temp_html, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    # Then use pandoc to convert HTML to PDF
                    result2 = subprocess.run([
                        'pandoc',
                        str(temp_html),
                        '-o', str(output_pdf),
                        '-f', 'html'
                    ], capture_output=True, text=True, timeout=30)
                    
                    # Clean up temp file
                    if temp_html.exists():
                        temp_html.unlink()
                    
                    if result2.returncode == 0 and output_pdf.exists():
                        return True
                    else:
                        print(f"Pandoc HTML fallback error: {result2.stderr}")
                        return False
                except Exception as e:
                    print(f"Pandoc HTML fallback exception: {e}")
                    return False
                    
        except subprocess.TimeoutExpired:
            print("Pandoc conversion timed out")
            return False
        except Exception as e:
            print(f"Pandoc error: {e}")
            return False
    
    def convert_with_weasyprint(self, output_pdf: Path,
                                temp_markdown: Path) -> bool:
        """Convert markdown to PDF using weasyprint.
        
        Args:
            output_pdf: Output PDF file path
            temp_markdown: Preprocessed markdown file path
            
        Returns:
            True if conversion successful, False otherwise
        """
        if not self.weasyprint_available:
            return False
            
        try:
            import weasyprint
            
            # Convert markdown to HTML (use preprocessed version)
            html_content = self.markdown_to_html(temp_markdown)
            
            # Convert HTML to PDF using weasyprint
            html_doc = weasyprint.HTML(string=html_content)
            html_doc.write_pdf(output_pdf)
            
            if output_pdf.exists():
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Weasyprint error: {e}")
            return False
    
    def convert(self, markdown_file: Path, output_pdf: Path) -> Optional[str]:
        """Convert Markdown file to PDF.
        
        Args:
            markdown_file: Path to the markdown file
            output_pdf: Path for the output PDF file
            
        Returns:
            Path to the created PDF file if successful, None otherwise
        """
        # Preprocess markdown to ensure no indentation
        temp_markdown = self.preprocess_markdown(markdown_file)
        
        try:
            # Try weasyprint first (pure Python solution)
            if self.weasyprint_available:
                if self.convert_with_weasyprint(output_pdf, temp_markdown):
                    return str(output_pdf)
            
            # If weasyprint fails or is not available, try pandoc
            if self.pandoc_available:
                if self.convert_with_pandoc(output_pdf, temp_markdown):
                    return str(output_pdf)
            
            # If both fail, suggest installation
            print("\nWarning: PDF conversion requires either weasyprint or pandoc.")
            print("Install weasyprint with: pip install weasyprint")
            print("Or install pandoc with: brew install pandoc")
            print("\nThe markdown file has been saved and can be manually converted to PDF.")
            
            return None
            
        finally:
            # Clean up temp file if still exists
            if temp_markdown.exists():
                temp_markdown.unlink()


def main():
    """Convert markdown files to PDF from command line."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to PDF with resume formatting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s resume.md
  %(prog)s resume.md -o output.pdf
  %(prog)s *.md -d output_dir/
  %(prog)s --check

Requirements:
  - weasyprint (recommended): pip install weasyprint
  - pandoc (fallback): brew install pandoc
        """
    )
    
    parser.add_argument(
        'files', 
        nargs='*', 
        help='Markdown file(s) to convert'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename (only for single file)'
    )
    parser.add_argument(
        '-d', '--output-dir',
        help='Output directory for PDFs'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if converters are installed'
    )
    
    args = parser.parse_args()
    
    converter = MarkdownToPDFConverter()
    
    
    # Check mode
    if args.check:
        print("Checking installed converters...")
        print(f"✓ weasyprint: {'Available' if converter.weasyprint_available else 'Not installed'}")
        print(f"✓ pandoc: {'Available' if converter.pandoc_available else 'Not installed'}")
        
        if not converter.pandoc_available and not converter.weasyprint_available:
            print("\n⚠️  No PDF converters found!")
            print("Install weasyprint with: pip install weasyprint")
            print("Or install pandoc with: brew install pandoc")
        return
    
    # Need files to convert
    if not args.files:
        parser.print_help()
        sys.exit(1)
    
    # Process files
    import glob
    all_files = []
    for pattern in args.files:
        all_files.extend(glob.glob(pattern))
    
    if not all_files:
        print(f"Error: No files found matching {args.files}")
        sys.exit(1)
    
    # Single file with custom output
    if len(all_files) == 1 and args.output:
        markdown_file = Path(all_files[0])
        output_pdf = Path(args.output)
        
        print(f"Converting {markdown_file.name} → {output_pdf.name}")
        result = converter.convert(markdown_file, output_pdf)
        
        if result:
            print(f"✓ Successfully converted to: {result}")
        else:
            print("✗ Conversion failed")
            sys.exit(1)
    
    # Multiple files or directory output
    else:
        output_dir = Path(args.output_dir) if args.output_dir else None
        if output_dir:
            output_dir.mkdir(exist_ok=True)
        
        success_count = 0
        for file_path in all_files:
            markdown_file = Path(file_path)
            
            if output_dir:
                output_pdf = output_dir / f"{markdown_file.stem}.pdf"
            else:
                output_pdf = markdown_file.with_suffix('.pdf')
            
            print(f"Converting {markdown_file.name} → {output_pdf.name}")
            result = converter.convert(markdown_file, output_pdf)
            
            if result:
                print(f"  ✓ Success: {output_pdf.name}")
                success_count += 1
            else:
                print(f"  ✗ Failed: {markdown_file.name}")
        
        print(f"\nConverted {success_count}/{len(all_files)} files successfully")


if __name__ == "__main__":
    main()