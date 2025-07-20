#!/usr/bin/env python3
"""
Debug Package Export Utility for BigShot

This script creates a comprehensive debug package containing:
- Application logs
- Environment variable snapshot (redacted)
- System information
- Configuration details

Usage:
    python scripts/export_debug_package.py [--output-dir /path/to/output]

Environment Variables:
    LOG_LEVEL: Set log level for the export process
    DEBUG_ZONE: Enable specific debug zones during export
"""

import argparse
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    parser = argparse.ArgumentParser(description='Export debug package for BigShot troubleshooting')
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='logs',
        help='Directory to save the debug package (default: logs)'
    )
    parser.add_argument(
        '--include-sensitive',
        action='store_true',
        help='Include sensitive environment variables (USE WITH CAUTION)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging during export'
    )
    
    args = parser.parse_args()
    
    # Set up minimal logging for the export process
    if args.verbose:
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['DEBUG_ZONE'] = 'export,env'
    
    try:
        # Import after setting up environment
        from app.utils.logging_config import create_debug_package_export, setup_logging
        
        # Initialize logging for export
        setup_logging(service_name='debug-export')
        
        print("Creating debug package export...")
        
        # Override sensitive data handling if requested
        if args.include_sensitive:
            print("WARNING: Including sensitive environment variables in export!")
            print("DO NOT share this package publicly!")
            import app.utils.logging_config as logging_config
            # This is a dangerous override - only for secure debugging
            original_create = logging_config.create_debug_package_export
            
            def create_debug_package_export_with_sensitive():
                result = original_create()
                # Re-create environment snapshot without redaction
                import json
                env_file = Path(result['package_path']).parent / 'temp_extract' / 'environment.json'
                if env_file.exists():
                    with open(env_file, 'w') as f:
                        json.dump(dict(os.environ), f, indent=2, sort_keys=True)
                return result
            
            result = create_debug_package_export_with_sensitive()
        else:
            result = create_debug_package_export()
        
        # Move to specified output directory if different
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        package_path = Path(result['package_path'])
        if package_path.parent != output_dir:
            new_path = output_dir / package_path.name
            package_path.rename(new_path)
            result['package_path'] = str(new_path)
        
        print(f"✓ Debug package created successfully!")
        print(f"  Location: {result['package_path']}")
        print(f"  Size: {result['size_bytes']:,} bytes")
        print(f"  Files included: {len(result['package_info']['files_included'])}")
        print("\nPackage contents:")
        for file_name in result['package_info']['files_included']:
            print(f"  - {file_name}")
        
        print("\nThis package can be shared with developers for troubleshooting.")
        if not args.include_sensitive:
            print("Sensitive information has been redacted for security.")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error creating debug package: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())