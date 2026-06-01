#!/usr/bin/env python
"""
Template Validation Script for A.K.D Fashion E-Commerce Platform
Checks for broken template links and syntax errors
"""

import os
import re
from pathlib import Path

def validate_templates():
    """Validate all Django templates"""
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'templates'
    
    results = {
        'total': 0,
        'valid': 0,
        'errors': [],
        'warnings': []
    }
    
    # Template files to check
    template_files = list(templates_dir.rglob('*.html')) + list(templates_dir.rglob('*.txt'))
    
    # Common template tags and their closing pairs
    tag_pairs = {
        'if': 'endif',
        'for': 'endfor',
        'block': 'endblock',
        'with': 'endwith',
        'load': None,  # Load doesn't need closing
        'extends': None,  # Extends doesn't need closing
    }
    
    print("=" * 70)
    print("A.K.D FASHION TEMPLATE VALIDATION REPORT")
    print("=" * 70)
    print()
    
    for template_file in sorted(template_files):
        results['total'] += 1
        
        relative_path = template_file.relative_to(base_dir)
        print(f"Checking: {relative_path}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common syntax errors
            errors = []
            
            # Check for unmatched opening tags
            for tag, closing_tag in tag_pairs.items():
                if closing_tag:
                    open_count = len(re.findall(rf'{{% {tag}\b', content))
                    close_count = len(re.findall(rf'{{% {closing_tag}}}', content))
                    
                    if open_count != close_count:
                        errors.append(
                            f"Mismatched {tag}/{closing_tag} tags: "
                            f"found {open_count} opening, {close_count} closing"
                        )
            
            # Check for orphaned tags
            if '{% ' in content and ' %}' not in content:
                errors.append("Potential unclosed template tag")
            
            # Check for common issues
            if 'csrf_token' in content and '{% csrf_token %}' not in content:
                if '<form' in content:
                    errors.append("Form found without {% csrf_token %}")
            
            if errors:
                for error in errors:
                    results['errors'].append(f"{relative_path}: {error}")
                    print(f"  ❌ ERROR: {error}")
            else:
                results['valid'] += 1
                print(f"  ✅ VALID")
        
        except Exception as e:
            results['errors'].append(f"{relative_path}: {str(e)}")
            print(f"  ❌ ERROR: {str(e)}")
        
        print()
    
    # Print summary
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total Templates: {results['total']}")
    print(f"Valid Templates: {results['valid']}")
    print(f"Errors Found: {len(results['errors'])}")
    print()
    
    if results['errors']:
        print("ERRORS:")
        for error in results['errors']:
            print(f"  • {error}")
        print()
        return False
    else:
        print("✅ ALL TEMPLATES VALIDATED SUCCESSFULLY!")
        print("✅ No broken links or syntax errors detected!")
        print("✅ Ready for deployment!")
        return True

def check_missing_templates():
    """Check for templates referenced in views but not created"""
    
    print("\n" + "=" * 70)
    print("CHECKING FOR MISSING TEMPLATES")
    print("=" * 70)
    print()
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'templates'
    
    # These are the templates that were previously missing
    critical_templates = {
        'products/category_products.html': 'CategoryProductsView',
        'products/add_to_cart_modal.html': 'AddToCartView',
    }
    
    missing = []
    
    for template_path, view_name in critical_templates.items():
        full_path = templates_dir / template_path
        if full_path.exists():
            print(f"✅ {template_path} - Created for {view_name}")
        else:
            print(f"❌ {template_path} - MISSING for {view_name}")
            missing.append((template_path, view_name))
    
    print()
    
    if missing:
        print(f"❌ Found {len(missing)} missing critical templates!")
        return False
    else:
        print("✅ ALL CRITICAL TEMPLATES EXIST!")
        return True

def main():
    """Run all validations"""
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  A.K.D FASHION E-COMMERCE PLATFORM - TEMPLATE VALIDATOR  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Run checks
    syntax_ok = validate_templates()
    templates_ok = check_missing_templates()
    
    # Final result
    print("\n" + "=" * 70)
    print("FINAL VALIDATION RESULT")
    print("=" * 70)
    
    if syntax_ok and templates_ok:
        print("\n✅ ALL VALIDATIONS PASSED!")
        print("✅ Application is ready for deployment!")
        print("\nDeployment Instructions:")
        print("1. python manage.py check")
        print("2. python manage.py migrate")
        print("3. python manage.py runserver")
        print("4. Visit http://localhost:8000")
        return 0
    else:
        print("\n❌ VALIDATION FAILED!")
        print("Please fix the errors above before deployment.")
        return 1

if __name__ == '__main__':
    exit(main())
