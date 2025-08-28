module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation changes
        'style',    // Code style changes (formatting, etc.)
        'refactor', // Code refactoring
        'perf',     // Performance improvements
        'test',     // Adding or updating tests
        'chore',    // Maintenance tasks
        'ci',       // CI/CD changes
        'build',    // Build system changes
        'revert',   // Reverting changes
        'security', // Security fixes
        'deps',     // Dependency updates
        'config',   // Configuration changes
        'release'   // Release commits
      ]
    ],
    'scope-enum': [
      2,
      'always',
      [
        'api',        // Backend API changes
        'web',        // Frontend web app changes
        'worker',     // Worker service changes
        'docker',     // Docker configuration
        'k8s',        // Kubernetes configuration
        'ci',         // CI/CD pipeline
        'docs',       // Documentation
        'deps',       // Dependencies
        'config',     // Configuration files
        'auth',       // Authentication
        'invoice',    // Invoice functionality
        'facturx',    // Factur-X specific features
        'pdf',        // PDF generation
        'xml',        // XML processing
        'validation', // Validation logic
        'ui',         // User interface
        'db',         // Database
        'security',   // Security features
        'monitoring', // Monitoring and logging
        'infra',      // Infrastructure
        'test',       // Testing
        'lint',       // Linting
        'format'      // Code formatting
      ]
    ],
    'subject-case': [2, 'always', 'sentence-case'],
    'subject-max-length': [2, 'always', 100],
    'subject-min-length': [2, 'always', 10],
    'header-max-length': [2, 'always', 120],
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [2, 'always'],
    'body-max-line-length': [2, 'always', 100],
    'footer-max-line-length': [2, 'always', 100]
  },
  helpUrl: 'https://github.com/conventional-changelog/commitlint/#what-is-commitlint'
};