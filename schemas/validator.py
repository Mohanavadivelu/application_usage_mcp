"""
MCP Protocol Schema Validation Utilities
"""
import json
import jsonschema
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SchemaValidator:
    def __init__(self):
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all JSON schemas from the schemas directory"""
        schema_dir = os.path.dirname(__file__)
        schema_files = {
            "initialize_request": "initialize_request.json",
            "tool_call_request": "tool_call_request.json",
            "resource_read_request": "resource_read_request.json"
        }
        
        for schema_name, file_name in schema_files.items():
            schema_path = os.path.join(schema_dir, file_name)
            try:
                with open(schema_path, 'r') as f:
                    self.schemas[schema_name] = json.load(f)
                logger.debug(f"Loaded schema: {schema_name}")
            except Exception as e:
                logger.error(f"Failed to load schema {schema_name}: {e}")
    
    def validate_message(self, message: Dict[str, Any], schema_name: str) -> Optional[str]:
        """
        Validate a message against a schema
        
        Args:
            message: The message to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            None if valid, error message if invalid
        """
        if schema_name not in self.schemas:
            return f"Unknown schema: {schema_name}"
        
        try:
            jsonschema.validate(message, self.schemas[schema_name])
            return None
        except jsonschema.ValidationError as e:
            return f"Validation error: {e.message}"
        except Exception as e:
            return f"Schema validation failed: {e}"
    
    def validate_initialize_request(self, message: Dict[str, Any]) -> Optional[str]:
        """Validate an initialize request"""
        return self.validate_message(message, "initialize_request")
    
    def validate_tool_call_request(self, message: Dict[str, Any]) -> Optional[str]:
        """Validate a tool call request"""
        return self.validate_message(message, "tool_call_request")
    
    def validate_resource_read_request(self, message: Dict[str, Any]) -> Optional[str]:
        """Validate a resource read request"""
        return self.validate_message(message, "resource_read_request")


# Global validator instance
validator = SchemaValidator()
