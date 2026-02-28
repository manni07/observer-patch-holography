#!/usr/bin/env python3
"""
Preprocess PAPER.md for pandoc -> LaTeX -> PDF conversion.
Strategy:
  1. Minimal markdown preprocessing (structure only)
  2. Let pandoc do all markdown->LaTeX conversion
  3. Fix Unicode in the LaTeX output (post-processing)
"""
import re
import sys
import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "paper")
PAPER = os.path.join(DIR, "PAPER.md")
OUTPUT_MD = os.path.join(DIR, "PAPER_processed.md")
OUTPUT_TEX = os.path.join(DIR, "PAPER_processed.tex")
OUTPUT_PDF = os.path.join(DIR, "PAPER.pdf")
TEMPLATE = os.path.join(DIR, "template.tex")


def convert_abstract_to_latex(abstract_md):
    """Convert abstract markdown to LaTeX via pandoc."""
    result = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'latex', '--wrap=preserve'],
        input=abstract_md, capture_output=True, text=True
    )
    return result.stdout.strip()


def fix_display_math_blocks(text):
    """Ensure $$ blocks have no blank lines inside."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == '$$':
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines) and lines[j].strip() != '$$':
                math_lines = []
                while j < len(lines):
                    if lines[j].strip() == '$$':
                        break
                    if lines[j].strip() != '':
                        math_lines.append(lines[j])
                    j += 1
                if result and result[-1].strip() != '':
                    result.append('')
                result.append('$$')
                result.extend(math_lines)
                result.append('$$')
                result.append('')
                i = j + 1
                continue
        result.append(lines[i])
        i += 1
    return '\n'.join(result)


def preprocess_markdown(text):
    """Minimal markdown preprocessing - structure only."""
    # Extract abstract
    abstract_match = re.search(
        r'^## Abstract\s*\n(.*?)(?=^## Table of Contents)',
        text, re.MULTILINE | re.DOTALL
    )
    abstract_latex = ""
    if abstract_match:
        abstract_md = abstract_match.group(1).strip()
        abstract_latex = convert_abstract_to_latex(abstract_md)
        text = text[:abstract_match.start()] + text[abstract_match.end():]

    # Remove title
    text = re.sub(r'^# Observer-Patch Holography\s*\n', '', text, count=1,
                  flags=re.MULTILINE)

    # Remove TOC
    text = re.sub(
        r'^## Table of Contents\s*\n.*?(?=^---\s*$)',
        '', text, count=1, flags=re.MULTILINE | re.DOTALL
    )

    # Remove leading horizontal rules
    text = re.sub(r'^---\s*\n', '\n', text, count=2, flags=re.MULTILINE)

    # Remove manual section numbers
    text = re.sub(r'^(#{2})\s*\d+\.\s+', r'\1 ', text, flags=re.MULTILINE)
    text = re.sub(r'^(#{3})\s*\d+\.\d+\s+', r'\1 ', text, flags=re.MULTILINE)
    text = re.sub(r'^(#{4})\s*\d+\.\d+\.\d+\s+', r'\1 ', text, flags=re.MULTILINE)

    # Fix display math blocks
    text = fix_display_math_blocks(text)

    # YAML header
    yaml = '---\ntitle: "Observer-Patch Holography"\n---\n\n'

    return yaml + text, abstract_latex


# LaTeX-level Unicode replacements (applied to .tex output)
LATEX_UNICODE_REPLACEMENTS = {
    # Arrows
    '⟹': r'\ensuremath{\Longrightarrow}',
    '⟸': r'\ensuremath{\Longleftarrow}',
    '→': r'\ensuremath{\to}',
    '←': r'\ensuremath{\leftarrow}',
    '↔': r'\ensuremath{\leftrightarrow}',
    '⇒': r'\ensuremath{\Rightarrow}',
    '⇐': r'\ensuremath{\Leftarrow}',
    # Comparison/relation
    '≠': r'\ensuremath{\neq}',
    '≡': r'\ensuremath{\equiv}',
    '≤': r'\ensuremath{\leq}',
    '≥': r'\ensuremath{\geq}',
    '≈': r'\ensuremath{\approx}',
    '≲': r'\ensuremath{\lesssim}',
    '≳': r'\ensuremath{\gtrsim}',
    '∼': r'\ensuremath{\sim}',
    '≅': r'\ensuremath{\cong}',
    '≪': r'\ensuremath{\ll}',
    '≫': r'\ensuremath{\gg}',
    '∝': r'\ensuremath{\propto}',
    # Operators
    '×': r'\ensuremath{\times}',
    '±': r'\ensuremath{\pm}',
    '∞': r'\ensuremath{\infty}',
    '∫': r'\ensuremath{\int}',
    '∑': r'\ensuremath{\sum}',
    '∏': r'\ensuremath{\prod}',
    '√': r'\ensuremath{\sqrt{}}',
    '∂': r'\ensuremath{\partial}',
    '∈': r'\ensuremath{\in}',
    '†': r'\ensuremath{\dagger}',
    '−': r'\ensuremath{-}',
    '·': r'\ensuremath{\cdot}',
    # Set operations
    '∩': r'\ensuremath{\cap}',
    '∪': r'\ensuremath{\cup}',
    '⊂': r'\ensuremath{\subset}',
    '⊃': r'\ensuremath{\supset}',
    '⊆': r'\ensuremath{\subseteq}',
    '⊇': r'\ensuremath{\supseteq}',
    '⊕': r'\ensuremath{\oplus}',
    '⊗': r'\ensuremath{\otimes}',
    # Greek lowercase
    'α': r'\ensuremath{\alpha}',
    'β': r'\ensuremath{\beta}',
    'γ': r'\ensuremath{\gamma}',
    'δ': r'\ensuremath{\delta}',
    'ε': r'\ensuremath{\varepsilon}',
    'ζ': r'\ensuremath{\zeta}',
    'η': r'\ensuremath{\eta}',
    'θ': r'\ensuremath{\theta}',
    'ι': r'\ensuremath{\iota}',
    'κ': r'\ensuremath{\kappa}',
    'λ': r'\ensuremath{\lambda}',
    'μ': r'\ensuremath{\mu}',
    'ν': r'\ensuremath{\nu}',
    'ξ': r'\ensuremath{\xi}',
    'π': r'\ensuremath{\pi}',
    'ρ': r'\ensuremath{\rho}',
    'σ': r'\ensuremath{\sigma}',
    'τ': r'\ensuremath{\tau}',
    'υ': r'\ensuremath{\upsilon}',
    'φ': r'\ensuremath{\varphi}',
    'χ': r'\ensuremath{\chi}',
    'ψ': r'\ensuremath{\psi}',
    'ω': r'\ensuremath{\omega}',
    # Greek uppercase
    'Γ': r'\ensuremath{\Gamma}',
    'Δ': r'\ensuremath{\Delta}',
    'Θ': r'\ensuremath{\Theta}',
    'Λ': r'\ensuremath{\Lambda}',
    'Ξ': r'\ensuremath{\Xi}',
    'Π': r'\ensuremath{\Pi}',
    'Σ': r'\ensuremath{\Sigma}',
    'Φ': r'\ensuremath{\Phi}',
    'Ψ': r'\ensuremath{\Psi}',
    'Ω': r'\ensuremath{\Omega}',
    # Script/fancy
    '𝒜': r'\ensuremath{\mathcal{A}}',
    '𝒞': r'\ensuremath{\mathcal{C}}',
    '𝒪': r'\ensuremath{\mathcal{O}}',
    'ℋ': r'\ensuremath{\mathcal{H}}',
    'ℂ': r'\ensuremath{\mathbb{C}}',
    'ℤ': r'\ensuremath{\mathbb{Z}}',
    'ℓ': r'\ensuremath{\ell}',
    'ℏ': r'\ensuremath{\hbar}',
    # Symbols
    '☉': r'\ensuremath{\odot}',
    '✓': r'\checkmark',
    '⟨': r'\ensuremath{\langle}',
    '⟩': r'\ensuremath{\rangle}',
    '∣': r'\ensuremath{|}',
    '∥': r'\ensuremath{\|}',
    '□': r'\ensuremath{\square}',
    # Modifier/superscript letters
    'ᶜ': r'\textsuperscript{c}',
    # Box drawing (just remove)
    '─': '-',
    '═': '=',
    # Typography
    '…': r'\ldots{}',
    '—': '---',
    '–': '--',
    '\u201C': '``',
    '\u201D': "''",
    '\u2018': '`',
    '\u2019': "'",
    '′': "'",
    '″': "''",
    # Accented chars
    'Č': r'\v{C}',
    'č': r'\v{c}',
    'ŝ': r'\^{s}',
    'Ũ': r'\~{U}',
    'ü': r'\"u',
    'ö': r'\"o',
    'ä': r'\"a',
    'é': r"\'e",
    'è': r'\`e',
    'ñ': r'\~n',
}


def replace_unicode_superscripts_in_tex(tex):
    """Replace Unicode super/subscript digits in LaTeX output."""
    sup_map = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
        '⁺': '+', '⁻': '-', '⁽': '(', '⁾': ')', 'ⁿ': 'n',
    }
    sub_map = {
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
        '₊': '+', '₋': '-',
    }

    sup_chars = ''.join(re.escape(c) for c in sup_map.keys())
    def sup_repl(m):
        digits = ''.join(sup_map.get(c, c) for c in m.group(0))
        return r'\textsuperscript{' + digits + '}'
    tex = re.sub(f'[{sup_chars}]+', sup_repl, tex)

    sub_chars = ''.join(re.escape(c) for c in sub_map.keys())
    def sub_repl(m):
        digits = ''.join(sub_map.get(c, c) for c in m.group(0))
        return r'\textsubscript{' + digits + '}'
    tex = re.sub(f'[{sub_chars}]+', sub_repl, tex)

    return tex


def post_process_tex(tex, abstract_latex):
    """Comprehensive post-processing of the generated .tex file."""

    # 1. Insert abstract
    if abstract_latex:
        abstract_block = "\\begin{abstract}\n" + abstract_latex + "\n\\end{abstract}\n"
        tex = tex.replace("\\maketitle", "\\maketitle\n\n" + abstract_block)

    # 2. Convert $$...$$ to \[...\]
    def fix_display_math(match):
        content = match.group(1).strip()
        content = re.sub(r'\n\s*\n', '\n', content)
        return '\\[\n' + content + '\n\\]'
    tex = re.sub(r'\$\$\s*\n(.*?)\n\s*\$\$', fix_display_math, tex, flags=re.DOTALL)
    tex = re.sub(r'\$\$([^$]+?)\$\$', r'\\[\1\\]', tex)

    # 3. Fix stray \rm
    tex = re.sub(r'\{\\rm\s+(\w+)\}', r'\\mathrm{\1}', tex)

    # 4. Replace Unicode superscripts/subscripts
    tex = replace_unicode_superscripts_in_tex(tex)

    # 5. Replace all other Unicode characters
    for char, replacement in LATEX_UNICODE_REPLACEMENTS.items():
        tex = tex.replace(char, replacement)

    # 6. Fix escaped underscores/carets next to math content
    # Pandoc outputs: \ensuremath{X}\_\{Y\} for text like "Λ_{QCD}"
    # and X\_Y for text like "n_f"
    # We need to convert these to proper math mode

    # Pattern: \ensuremath{X}\_\{Y\}\^{}\{Z\} -> $X_{Y}^{Z}$
    tex = re.sub(
        r'\\ensuremath\{([^}]+)\}\\_\\\{([^}]*)\\\}\\[\\^]\{\}\\\{([^}]*)\\\}',
        r'$\1_{\2}^{\3}$',
        tex
    )
    # Pattern: \ensuremath{X}\_\{Y\} -> $X_{Y}$
    tex = re.sub(
        r'\\ensuremath\{([^}]+)\}\\_\\\{([^}]*)\\\}',
        r'$\1_{\2}$',
        tex
    )
    # Pattern: \ensuremath{X}\_Y -> $X_Y$
    tex = re.sub(
        r'\\ensuremath\{([^}]+)\}\\_([a-zA-Z0-9])',
        r'$\1_\2$',
        tex
    )
    # Pattern: X\_\{Y\} -> $X_{Y}$ (plain letter with escaped subscript)
    tex = re.sub(
        r'(?<![\\a-zA-Z])([a-zA-Z])\\_\\\{([^}]*)\\\}',
        r'$\1_{\2}$',
        tex
    )
    # Pattern: X\_Y -> $X_Y$ (plain letter with escaped subscript)
    tex = re.sub(
        r'(?<![\\a-zA-Z])([a-zA-Z])\\_([a-zA-Z0-9])(?=[^a-zA-Z]|$)',
        r'$\1_\2$',
        tex
    )
    # Fix \^{}\{...\} -> $^{...}$ (escaped superscripts)
    tex = re.sub(
        r'\\\^\{\}\\\{([^}]*)\\\}',
        r'$^{\1}$',
        tex
    )
    # Merge adjacent math delimiters: $...$  $...$ -> $... ...$
    tex = re.sub(r'\$\s*\$', ' ', tex)

    # 6b. Handle remaining combining chars
    tex = tex.replace('ʸ', r'\textsuperscript{y}')
    tex = tex.replace('\u0302', r'\^{}')  # combining circumflex
    tex = tex.replace('\u0304', r'\={}')  # combining macron

    # 7. Check for remaining problematic Unicode
    remaining = set()
    for i, c in enumerate(tex):
        if ord(c) > 0x7F and c not in '\n\r\t':
            # Allow common Latin-1 chars that T1 can handle
            if ord(c) < 0x100:
                continue
            remaining.add((c, hex(ord(c))))
    if remaining:
        print(f"  Note: {len(remaining)} non-ASCII chars remain (may be OK):")
        for c, h in sorted(remaining, key=lambda x: x[1])[:15]:
            print(f"    {h}: {c!r}")

    return tex


def main():
    with open(PAPER, 'r') as f:
        text = f.read()

    processed, abstract_latex = preprocess_markdown(text)

    with open(OUTPUT_MD, 'w') as f:
        f.write(processed)

    # Step 1: Generate .tex
    print("Step 1: Generating LaTeX via pandoc...")
    cmd_tex = [
        'pandoc', OUTPUT_MD,
        '-o', OUTPUT_TEX,
        '--template', TEMPLATE,
        '--number-sections',
        '--toc',
        '--wrap=preserve',
    ]
    result = subprocess.run(cmd_tex, capture_output=True, text=True, cwd=DIR)
    if result.returncode != 0:
        print("Pandoc error:", result.stderr[:3000])

    # Step 2: Post-process
    print("Step 2: Post-processing LaTeX...")
    with open(OUTPUT_TEX, 'r') as f:
        tex = f.read()
    tex = post_process_tex(tex, abstract_latex)
    with open(OUTPUT_TEX, 'w') as f:
        f.write(tex)

    # Step 3: Compile
    print("Step 3: Compiling with tectonic...")
    result = subprocess.run(
        ['tectonic', '-X', 'compile', OUTPUT_TEX],
        capture_output=True, text=True, cwd=DIR
    )

    if result.returncode != 0:
        print("Tectonic errors:")
        for line in result.stderr.split('\n'):
            if 'error:' in line.lower():
                print("  >>", line)
        sys.exit(1)
    else:
        generated = OUTPUT_TEX.replace('.tex', '.pdf')
        if os.path.exists(generated) and generated != OUTPUT_PDF:
            os.rename(generated, OUTPUT_PDF)
        warnings = result.stderr.count('warning:')
        missing_chars = result.stderr.count('Missing character')
        print(f"Success! PDF written to {OUTPUT_PDF}")
        if warnings:
            print(f"  ({warnings} warnings, {missing_chars} missing characters)")


if __name__ == '__main__':
    main()
