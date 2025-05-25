#!/usr/bin/env python3
"""
LaTeX Validation and Fixing Script

This script validates and fixes common LaTeX issues that prevent PDF compilation.
"""

import re
import os
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict

class LaTeXValidator:
    def __init__(self):
        self.common_errors = []
        
    def validate_braces(self, content: str) -> List[str]:
        """Check for matching braces in LaTeX content."""
        errors = []
        open_braces = 0
        line_num = 0
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Skip comments
            if line.strip().startswith('%'):
                continue
                
            # Count braces
            for char in line:
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                    
            if open_braces < 0:
                errors.append(f"Line {line_num}: Extra closing brace")
                open_braces = 0  # Reset to continue checking
                
        if open_braces > 0:
            errors.append(f"Missing {open_braces} closing brace(s)")
        elif open_braces < 0:
            errors.append(f"Extra {-open_braces} closing brace(s)")
            
        return errors
    
    def fix_special_characters(self, content: str) -> str:
        """Fix unescaped special characters in LaTeX."""
        # Special characters that need escaping in LaTeX
        special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '^': r'\^{}',
            '~': r'\~{}',
        }
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip LaTeX commands and comments
            if line.strip().startswith('\\') or line.strip().startswith('%'):
                fixed_lines.append(line)
                continue
            
            # Process text in \Bullet{} commands specially
            if '\\Bullet{' in line:
                # Extract and fix content within \Bullet{}
                bullet_pattern = r'\\Bullet\{([^}]*)\}'
                
                def fix_bullet_content(match):
                    content = match.group(1)
                    # Don't escape characters in \href commands
                    if '\\href' not in content:
                        for char, escaped in special_chars.items():
                            # Don't re-escape already escaped characters
                            if f'\\{char}' not in content:
                                content = re.sub(f'(?<!\\\\){re.escape(char)}', escaped, content)
                    return f'\\Bullet{{{content}}}'
                
                line = re.sub(bullet_pattern, fix_bullet_content, line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_encoding_issues(self, content: str) -> str:
        """Fix common encoding issues."""
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '—': '--',
            '–': '-',
            '…': '...',
            '™': '',
            '®': '',
            '©': '',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        return content
    
    def validate_commands(self, content: str) -> List[str]:
        """Check for undefined LaTeX commands."""
        errors = []
        
        # Common undefined command patterns
        undefined_patterns = [
            (r'\\Bullet\s*\{', 'Missing \\newcommand{\\Bullet} definition'),
            (r'\\titleformat\s*\{', 'Missing titlesec package'),
            (r'\\href\s*\{', 'Missing hyperref package'),
        ]
        
        for pattern, error_msg in undefined_patterns:
            if re.search(pattern, content):
                # Check if the command is defined
                if pattern == r'\\Bullet\s*\{' and '\\newcommand{\\Bullet}' not in content:
                    errors.append(error_msg)
                    
        return errors
    
    def fix_bullet_command(self, content: str) -> str:
        """Ensure \Bullet command is properly defined."""
        if '\\Bullet{' in content and '\\newcommand{\\Bullet}' not in content:
            # Add the command definition after \begin{document}
            content = content.replace(
                '\\begin{document}',
                '\\begin{document}\n\\newcommand{\\Bullet}{\\raisebox{-2pt}{\\tiny $\\bullet$}\\hspace{8pt}}'
            )
        return content
    
    def fix_tabular_issues(self, content: str) -> str:
        """Fix common tabular environment issues."""
        # Fix incomplete tabular commands
        lines = content.split('\n')
        fixed_lines = []
        in_tabular = False
        
        for i, line in enumerate(lines):
            # Check for tabular start
            if '\\begin{tabular' in line:
                in_tabular = True
                # Ensure the line ends properly
                if not line.rstrip().endswith('}'):
                    # Try to find the closing brace on the next line
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('{'):
                        line = line.rstrip() + lines[i + 1].strip()
                        lines[i + 1] = ''  # Clear the next line
                        
            # Check for tabular end
            if '\\end{tabular' in line:
                in_tabular = False
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
    
    def validate_and_fix(self, latex_file: str) -> Tuple[str, List[str]]:
        """Validate and fix a LaTeX file."""
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        errors = []
        
        # Apply fixes
        content = self.fix_encoding_issues(content)
        content = self.fix_special_characters(content)
        content = self.fix_bullet_command(content)
        content = self.fix_tabular_issues(content)
        
        # Validate
        errors.extend(self.validate_braces(content))
        errors.extend(self.validate_commands(content))
        
        return content, errors
    
    def compile_latex(self, latex_file: str, output_dir: str = None) -> Tuple[bool, str]:
        """Try to compile a LaTeX file and return success status and error message."""
        if output_dir is None:
            output_dir = os.path.dirname(latex_file)
            
        try:
            result = subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', output_dir,
                latex_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, "Success"
            else:
                # Extract error from output
                error_msg = ""
                if "! " in result.stdout:
                    error_lines = result.stdout.split('\n')
                    for i, line in enumerate(error_lines):
                        if line.startswith('! '):
                            error_msg = line
                            # Get a few lines of context
                            for j in range(i+1, min(i+5, len(error_lines))):
                                if error_lines[j].strip():
                                    error_msg += "\n" + error_lines[j]
                            break
                return False, error_msg or result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "LaTeX compilation timed out"
        except Exception as e:
            return False, str(e)

def main():
    """Process all LaTeX files that failed to convert to PDF."""
    latex_dir = Path("tailored_resumes_latex")
    pdf_dir = Path("tailored_resumes_pdf")
    
    # Get all LaTeX files
    latex_files = list(latex_dir.glob("*.tex"))
    
    # Get all PDF files (to identify which LaTeX files succeeded)
    pdf_files = {f.stem for f in pdf_dir.glob("*.pdf")}
    
    # Find LaTeX files without corresponding PDFs
    failed_files = [f for f in latex_files if f.stem not in pdf_files]
    
    print(f"Found {len(latex_files)} LaTeX files")
    print(f"Found {len(pdf_files)} PDF files")
    print(f"Found {len(failed_files)} failed conversions\n")
    
    if not failed_files:
        print("All LaTeX files have been successfully converted to PDF!")
        return
    
    validator = LaTeXValidator()
    
    # Process each failed file
    for latex_file in failed_files[:5]:  # Process first 5 to avoid too many
        print(f"\n{'='*60}")
        print(f"Processing: {latex_file.name}")
        print(f"{'='*60}")
        
        # Validate and fix
        fixed_content, errors = validator.validate_and_fix(str(latex_file))
        
        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"  - {error}")
        
        # Save fixed version
        fixed_file = latex_file.parent / f"fixed_{latex_file.name}"
        with open(fixed_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Try to compile
        print(f"\nTrying to compile fixed version...")
        success, error_msg = validator.compile_latex(str(fixed_file), str(pdf_dir))
        
        if success:
            print(f"✓ Successfully compiled to PDF!")
            # Replace original with fixed version
            os.rename(fixed_file, latex_file)
        else:
            print(f"✗ Compilation failed: {error_msg}")
            # Keep the fixed file for debugging
            print(f"Fixed file saved as: {fixed_file.name}")

if __name__ == "__main__":
    main()