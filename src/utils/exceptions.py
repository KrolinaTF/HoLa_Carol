class ExpertSystemException(Exception):
    """Base exception for the expert system"""
    pass

class KnowledgeBaseError(ExpertSystemException):
    """Error accessing or processing knowledge base"""
    pass

class AgentError(ExpertSystemException):
    """Error in agent processing"""
    pass

class ValidationError(ExpertSystemException):
    """Error in validation process"""
    pass

class LLMError(ExpertSystemException):
    """Error in LLM processing"""
    pass

class DatabaseError(ExpertSystemException):
    """Error in database operations"""
    pass

class AuthenticationError(ExpertSystemException):
    """Error in authentication process"""
    pass

class ConfigurationError(ExpertSystemException):
    """Error in system configuration"""
    pass