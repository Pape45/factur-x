# AI Prompts & Templates Library

## Overview
This document contains reusable prompts, templates, and AI assistance patterns for the Factur-X Express project development.

---

## Development Prompts

### Code Review Prompt
```
Please review this code for the Factur-X Express project:

[CODE_BLOCK]

Focus on:
1. **Factur-X Compliance**: Ensure EN 16931 standard adherence
2. **Security**: Check for vulnerabilities (OWASP Top 10)
3. **Performance**: Identify potential bottlenecks
4. **Code Quality**: Follow Python/TypeScript best practices
5. **Error Handling**: Robust error scenarios coverage
6. **Testing**: Suggest test cases for critical paths

Context: This is part of [COMPONENT_NAME] in our invoice generation system.
Priority: [P0/P1/P2]
Compliance Requirements: EN 16931, PDF/A-3, GDPR
```

### Architecture Design Prompt
```
Design a solution for [FEATURE_NAME] in the Factur-X Express system:

Requirements:
- [REQUIREMENT_1]
- [REQUIREMENT_2]
- [REQUIREMENT_3]

Constraints:
- Must integrate with existing FastAPI backend
- Should support 10,000+ concurrent users
- Must maintain EN 16931 compliance
- Follow microservices patterns where appropriate
- Consider AWS deployment (ECS, RDS, S3)

Please provide:
1. High-level architecture diagram (Mermaid)
2. Component breakdown with responsibilities
3. API design (endpoints, request/response)
4. Database schema changes (if needed)
5. Security considerations
6. Performance implications
7. Testing strategy
```

### Bug Investigation Prompt
```
Help investigate this bug in Factur-X Express:

**Bug Description**: [DESCRIPTION]
**Steps to Reproduce**: [STEPS]
**Expected Behavior**: [EXPECTED]
**Actual Behavior**: [ACTUAL]
**Environment**: [dev/staging/prod]
**Error Logs**: [LOGS]

System Context:
- Component: [COMPONENT_NAME]
- Related Features: [FEATURES]
- Recent Changes: [CHANGES]

Please analyze:
1. Root cause analysis
2. Potential fixes with pros/cons
3. Prevention strategies
4. Test cases to add
5. Monitoring improvements
```

### Performance Optimization Prompt
```
Optimize performance for [COMPONENT_NAME] in Factur-X Express:

Current Performance:
- Response Time: [TIME]
- Throughput: [REQUESTS/SEC]
- Resource Usage: [CPU/MEMORY]
- Bottlenecks: [IDENTIFIED_ISSUES]

Target Performance:
- Response Time: < 3 seconds
- Throughput: > 100 requests/sec
- Resource Usage: < 80% CPU, < 2GB memory

Constraints:
- Must maintain Factur-X compliance
- Cannot break existing API contracts
- Should be cost-effective
- Must be maintainable

Analyze and suggest:
1. Performance bottlenecks
2. Optimization strategies
3. Caching opportunities
4. Database query improvements
5. Code refactoring suggestions
6. Infrastructure scaling options
```

---

## Testing Prompts

### Test Case Generation Prompt
```
Generate comprehensive test cases for [FEATURE_NAME]:

Feature Description:
[FEATURE_DESCRIPTION]

Acceptance Criteria:
- [CRITERIA_1]
- [CRITERIA_2]
- [CRITERIA_3]

Please generate:
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test endpoint behavior
4. **Edge Cases**: Boundary conditions and error scenarios
5. **Performance Tests**: Load and stress testing scenarios
6. **Security Tests**: Authentication, authorization, input validation
7. **Compliance Tests**: EN 16931 and PDF/A-3 validation

Format: pytest-compatible test functions with descriptive names and docstrings.
```

### Compliance Testing Prompt
```
Create compliance test suite for Factur-X invoice generation:

Standards to Test:
- EN 16931 (European e-invoicing standard)
- PDF/A-3 (ISO 19005-3)
- French e-invoicing regulations

Test Categories:
1. **XML Structure**: Validate EN 16931 XML schema
2. **PDF Format**: Verify PDF/A-3 compliance
3. **Data Integrity**: Ensure XML-PDF consistency
4. **Mandatory Fields**: Check required invoice elements
5. **Business Rules**: Validate calculation logic
6. **Character Encoding**: UTF-8 compliance
7. **File Size**: Reasonable limits

Tools to Use:
- veraPDF for PDF/A-3 validation
- Mustangproject for EN 16931 validation
- Custom validators for business rules

Provide test cases with expected outcomes and validation criteria.
```

---

## Documentation Prompts

### API Documentation Prompt
```
Generate comprehensive API documentation for [ENDPOINT_NAME]:

Endpoint: [METHOD] [PATH]
Purpose: [DESCRIPTION]

Include:
1. **Overview**: Brief description and use cases
2. **Authentication**: Required auth method
3. **Parameters**: Path, query, and body parameters
4. **Request Examples**: Multiple scenarios with curl/JavaScript
5. **Response Examples**: Success and error responses
6. **Error Codes**: All possible error conditions
7. **Rate Limits**: Usage restrictions
8. **SDKs**: Code examples in Python and JavaScript

Format: OpenAPI 3.0 specification with rich examples.
Audience: External developers integrating with our API.
```

### User Guide Prompt
```
Create user guide section for [FEATURE_NAME]:

Target Audience: [SME finance managers / Developers / Freelancers]
Complexity Level: [Beginner / Intermediate / Advanced]

Structure:
1. **Overview**: What this feature does and why it's useful
2. **Prerequisites**: What users need before starting
3. **Step-by-Step Guide**: Detailed instructions with screenshots
4. **Common Use Cases**: Real-world scenarios
5. **Troubleshooting**: Common issues and solutions
6. **Best Practices**: Tips for optimal usage
7. **Related Features**: Links to complementary functionality

Tone: Friendly, professional, and helpful.
Format: Markdown with embedded images and code examples.
```

---

## Code Generation Templates

### FastAPI Endpoint Template
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import [ModelName]
from ..schemas import [SchemaName]Create, [SchemaName]Response
from ..auth import get_current_user
from ..services.[service_name] import [ServiceName]

router = APIRouter(prefix="/[endpoint]", tags="[tag]")

@router.post("/", response_model=[SchemaName]Response, status_code=status.HTTP_201_CREATED)
async def create_[resource](
    [resource]_data: [SchemaName]Create,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new [resource].
    
    - **[field]**: Description of field
    - **[field]**: Description of field
    """
    try:
        service = [ServiceName](db)
        result = await service.create_[resource]([resource]_data, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[[SchemaName]Response])
async def list_[resources](
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve a list of [resources] for the current user.
    """
    service = [ServiceName](db)
    return await service.get_[resources](current_user.id, skip, limit)

@router.get("/{[resource]_id}", response_model=[SchemaName]Response)
async def get_[resource](
    [resource]_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve a specific [resource] by ID.
    """
    service = [ServiceName](db)
    result = await service.get_[resource]([resource]_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="[Resource] not found"
        )
    return result
```

### Service Class Template
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from ..models.[model_name] import [ModelName]
from ..schemas.[schema_name] import [SchemaName]Create, [SchemaName]Update
from ..core.exceptions import ValidationError, NotFoundError
from ..core.logging import get_logger

logger = get_logger(__name__)

class [ServiceName]:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_[resource](
        self, 
        [resource]_data: [SchemaName]Create, 
        user_id: int
    ) -> [ModelName]:
        """
        Create a new [resource] for the specified user.
        
        Args:
            [resource]_data: The [resource] data to create
            user_id: The ID of the user creating the [resource]
            
        Returns:
            The created [resource] instance
            
        Raises:
            ValidationError: If the [resource] data is invalid
        """
        try:
            # Validate input data
            self._validate_[resource]_data([resource]_data)
            
            # Create new [resource]
            db_[resource] = [ModelName](
                **[resource]_data.dict(),
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            
            self.db.add(db_[resource])
            self.db.commit()
            self.db.refresh(db_[resource])
            
            logger.info(f"Created [resource] {db_[resource].id} for user {user_id}")
            return db_[resource]
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create [resource]: {str(e)}")
            raise
    
    async def get_[resource](
        self, 
        [resource]_id: int, 
        user_id: int
    ) -> Optional[[ModelName]]:
        """
        Retrieve a [resource] by ID for the specified user.
        """
        return self.db.query([ModelName]).filter(
            and_(
                [ModelName].id == [resource]_id,
                [ModelName].user_id == user_id
            )
        ).first()
    
    async def get_[resources](
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[[ModelName]]:
        """
        Retrieve a list of [resources] for the specified user.
        """
        return self.db.query([ModelName]).filter(
            [ModelName].user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def _validate_[resource]_data(self, data: [SchemaName]Create) -> None:
        """
        Validate [resource] data before creation.
        """
        # Add validation logic here
        if not data.[required_field]:
            raise ValidationError("[Required field] is required")
        
        # Add more validation as needed
```

### React Component Template
```typescript
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { [ServiceName] } from '../services/[serviceName]';
import { [TypeName] } from '../types/[typeName]';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorMessage } from '../components/ui/ErrorMessage';

interface [ComponentName]Props {
  [prop]: [type];
}

export const [ComponentName]: React.FC<[ComponentName]Props> = ({ [prop] }) => {
  const [formData, setFormData] = useState<Partial<[TypeName]>>({});
  const queryClient = useQueryClient();
  
  // Query for fetching data
  const {
    data: [dataName],
    isLoading,
    error
  } = useQuery({
    queryKey: ['[queryKey]', [prop]],
    queryFn: () => [ServiceName].get[Resource]([prop]),
    enabled: !![prop]
  });
  
  // Mutation for creating/updating
  const mutation = useMutation({
    mutationFn: [ServiceName].create[Resource],
    onSuccess: () => {
      toast.success('[Resource] created successfully!');
      queryClient.invalidateQueries({ queryKey: ['[queryKey]'] });
      setFormData({});
    },
    onError: (error: Error) => {
      toast.error(`Failed to create [resource]: ${error.message}`);
    }
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.[requiredField]) {
      toast.error('[Required field] is required');
      return;
    }
    mutation.mutate(formData as [TypeName]);
  };
  
  const handleInputChange = (field: keyof [TypeName], value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (error) {
    return <ErrorMessage message="Failed to load [resource]" />;
  }
  
  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        [Component Title]
      </h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            [Field Label]
          </label>
          <Input
            type="text"
            value={formData.[field] || ''}
            onChange={(e) => handleInputChange('[field]', e.target.value)}
            placeholder="Enter [field]"
            required
          />
        </div>
        
        <div className="flex justify-end space-x-3">
          <Button
            type="button"
            variant="secondary"
            onClick={() => setFormData({})}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={mutation.isPending}
            disabled={!formData.[requiredField]}
          >
            Create [Resource]
          </Button>
        </div>
      </form>
    </div>
  );
};
```

---

## Compliance Prompts

### EN 16931 Validation Prompt
```
Validate this invoice data against EN 16931 standard:

[INVOICE_DATA]

Check for:
1. **Mandatory Elements**: All required fields present
2. **Data Types**: Correct formats for dates, amounts, codes
3. **Business Rules**: VAT calculations, totals, etc.
4. **Code Lists**: Valid country codes, currency codes, etc.
5. **Cardinality**: Correct number of occurrences for each element
6. **Syntax Rules**: Proper structure and relationships

Provide:
- Validation results (pass/fail)
- Detailed error messages for failures
- Suggestions for fixing issues
- Compliance score (0-100%)
```

### PDF/A-3 Compliance Prompt
```
Analyze this PDF for PDF/A-3 compliance:

[PDF_FILE_INFO]

Validation Points:
1. **File Structure**: Valid PDF structure
2. **Metadata**: Required XMP metadata present
3. **Fonts**: All fonts embedded
4. **Colors**: Color space compliance
5. **Transparency**: No transparency usage
6. **Annotations**: Compliant annotation types
7. **Attachments**: Proper file attachment structure
8. **Encryption**: No encryption present

Use veraPDF validation and provide:
- Compliance status
- Detailed validation report
- Remediation steps for failures
```

---

## Deployment Prompts

### Infrastructure as Code Prompt
```
Generate Terraform configuration for Factur-X Express deployment:

Requirements:
- AWS ECS cluster with auto-scaling
- RDS PostgreSQL database (Multi-AZ)
- S3 bucket for file storage
- CloudFront CDN
- Application Load Balancer
- VPC with public/private subnets
- Security groups with minimal access
- IAM roles with least privilege

Environments: dev, staging, prod
Region: eu-west-1
Compliance: GDPR, SOC 2

Include:
1. Main infrastructure modules
2. Environment-specific variables
3. Security configurations
4. Monitoring and logging setup
5. Backup and disaster recovery
```

### CI/CD Pipeline Prompt
```
Create GitHub Actions workflow for Factur-X Express:

Pipeline Stages:
1. **Code Quality**: Linting, formatting, type checking
2. **Security**: SAST, dependency scanning
3. **Testing**: Unit, integration, compliance tests
4. **Build**: Docker image creation
5. **Deploy**: Environment-specific deployment
6. **Monitoring**: Health checks and notifications

Environments:
- dev: Auto-deploy on main branch
- staging: Auto-deploy on release branch
- prod: Manual approval required

Security:
- OIDC for AWS authentication
- Secrets management
- Vulnerability scanning
- Compliance checks
```

---

## Monitoring & Alerting Prompts

### Observability Setup Prompt
```
Design comprehensive observability for Factur-X Express:

Metrics to Track:
1. **Business Metrics**: Invoice generation rate, validation success rate
2. **Performance Metrics**: Response times, throughput, error rates
3. **Infrastructure Metrics**: CPU, memory, disk, network
4. **Security Metrics**: Failed logins, API abuse, vulnerabilities

Logging Strategy:
- Structured logging with correlation IDs
- Log levels and retention policies
- Sensitive data handling
- Compliance audit trails

Alerting Rules:
- Critical: System down, security breach
- Warning: High error rate, performance degradation
- Info: Deployment notifications, capacity alerts

Tools: Prometheus, Grafana, Sentry, CloudWatch
```

---

**Document Owner:** Development Team  
**Last Updated:** $(date)  
**Next Review:** Monthly or when new patterns emerge  
**Usage:** Copy and customize prompts for specific development tasks