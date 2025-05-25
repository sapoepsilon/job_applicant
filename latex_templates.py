#!/usr/bin/env python3
"""
LaTeX Templates for PDF Generation

This module contains LaTeX templates and utilities for converting
documents to PDF with specific formatting requirements.
"""

from pathlib import Path
from typing import Optional


class LaTeXTemplate:
    """Base class for LaTeX templates."""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_content(self) -> str:
        """Return the template content."""
        raise NotImplementedError
    
    def save_to_file(self, filepath: Path) -> Path:
        """Save template to a file."""
        with open(filepath, 'w') as f:
            f.write(self.get_content())
        return filepath


class ResumeTemplate(LaTeXTemplate):
    """LaTeX template for resume formatting with no bullet indentation."""
    
    def __init__(self):
        super().__init__("resume")
        
    def get_content(self) -> str:
        """Return the resume template content."""
        return r"""
\documentclass[11pt]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{fontspec}
\setmainfont{Helvetica Neue}
\usepackage{enumitem}
\setlist[itemize]{leftmargin=0pt,labelindent=0pt,labelsep=0.5em,itemsep=0pt,parsep=0pt}
\usepackage[hidelinks]{hyperref}

\begin{document}
$body$
\end{document}
"""


class ModernResumeTemplate(LaTeXTemplate):
    """Modern LaTeX template with custom colors and formatting."""
    
    def __init__(self):
        super().__init__("modern-resume")
        
    def get_content(self) -> str:
        """Return the modern resume template content."""
        return r"""
\documentclass[11pt]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{fontspec}
\setmainfont{Helvetica Neue}
\usepackage{xcolor}
\definecolor{linkcolor}{RGB}{0,102,204}
\usepackage{enumitem}
\setlist[itemize]{leftmargin=0pt,labelindent=0pt,labelsep=0.5em,itemsep=0pt,parsep=0pt}
\usepackage[colorlinks=true,linkcolor=linkcolor,urlcolor=linkcolor]{hyperref}

% Custom section formatting
\usepackage{titlesec}
\titleformat{\section}{\large\bfseries}{}{0pt}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries}{}{0pt}{}

\begin{document}
$body$
\end{document}
"""


class MinimalTemplate(LaTeXTemplate):
    """Minimal LaTeX template for simple documents."""
    
    def __init__(self):
        super().__init__("minimal")
        
    def get_content(self) -> str:
        """Return the minimal template content."""
        return r"""
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{fontspec}
\setmainfont{Arial}

\begin{document}
$body$
\end{document}
"""


class TemplateManager:
    """Manage LaTeX templates."""
    
    def __init__(self):
        self.templates = {
            'resume': ResumeTemplate(),
            'modern-resume': ModernResumeTemplate(),
            'minimal': MinimalTemplate()
        }
    
    def get_template(self, name: str = 'resume') -> Optional[LaTeXTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> list:
        """List available template names."""
        return list(self.templates.keys())
    
    def save_template(self, name: str, filepath: Path) -> Optional[Path]:
        """Save a template to file."""
        template = self.get_template(name)
        if template:
            return template.save_to_file(filepath)
        return None


# Pandoc command configurations for different use cases
PANDOC_CONFIGS = {
    'default': {
        'engine': 'xelatex',
        'variables': {
            'geometry': 'margin=0.75in',
            'fontsize': '11pt',
            'mainfont': 'Helvetica Neue',
            'urlcolor': 'blue',
            'linkcolor': 'blue'
        }
    },
    'resume': {
        'engine': 'xelatex',
        'variables': {
            'urlcolor': 'blue',
            'linkcolor': 'blue'
        }
    },
    'academic': {
        'engine': 'xelatex',
        'variables': {
            'geometry': 'margin=1in',
            'fontsize': '12pt',
            'mainfont': 'Times New Roman',
            'urlcolor': 'black',
            'linkcolor': 'black',
            'documentclass': 'article',
            'classoption': '12pt'
        }
    }
}


def get_pandoc_command(config_name: str = 'default') -> dict:
    """Get pandoc configuration by name."""
    return PANDOC_CONFIGS.get(config_name, PANDOC_CONFIGS['default'])


def build_pandoc_args(input_file: str, output_file: str, 
                      template_file: Optional[str] = None,
                      config_name: str = 'default') -> list:
    """Build pandoc command line arguments."""
    config = get_pandoc_command(config_name)
    
    args = [
        'pandoc',
        input_file,
        '-o', output_file,
        '--pdf-engine=' + config['engine']
    ]
    
    if template_file:
        args.extend(['--template', template_file])
    
    # Add variables
    for key, value in config['variables'].items():
        args.extend(['-V', f'{key}={value}'])
    
    return args


def main():
    """Command line interface for LaTeX templates."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='LaTeX Template Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    # List available templates
  %(prog)s --show resume             # Show template content
  %(prog)s --save resume output.tex  # Save template to file
  %(prog)s --preview resume          # Show pandoc command for template
        """
    )
    
    parser.add_argument('--list', action='store_true', help='List available templates')
    parser.add_argument('--show', metavar='NAME', help='Show template content')
    parser.add_argument('--save', nargs=2, metavar=('NAME', 'FILE'), 
                        help='Save template to file')
    parser.add_argument('--preview', metavar='NAME', 
                        help='Show pandoc command for template')
    
    args = parser.parse_args()
    
    manager = TemplateManager()
    
    if args.list:
        print("Available LaTeX templates:")
        for name in manager.list_templates():
            template = manager.get_template(name)
            print(f"  {name:<15} - {template.__class__.__doc__.strip()}")
    
    elif args.show:
        template = manager.get_template(args.show)
        if template:
            print(f"Template: {args.show}")
            print("-" * 60)
            print(template.get_content())
        else:
            print(f"Error: Template '{args.show}' not found")
            print(f"Available templates: {', '.join(manager.list_templates())}")
    
    elif args.save:
        name, filepath = args.save
        saved = manager.save_template(name, Path(filepath))
        if saved:
            print(f"✓ Saved {name} template to: {filepath}")
        else:
            print(f"Error: Template '{name}' not found")
            print(f"Available templates: {', '.join(manager.list_templates())}")
    
    elif args.preview:
        if args.preview in manager.list_templates():
            args_list = build_pandoc_args(
                'input.md', 'output.pdf', 
                f'{args.preview}_template.tex',
                config_name='resume' if args.preview == 'resume' else 'default'
            )
            print(f"Pandoc command for '{args.preview}' template:")
            print(" ".join(args_list))
        else:
            print(f"Error: Template '{args.preview}' not found")
            print(f"Available templates: {', '.join(manager.list_templates())}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()