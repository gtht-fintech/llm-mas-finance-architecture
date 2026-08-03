name: Bug Report
description: Report a bug in the L4 governance layer, evaluation framework, or other component
title: "[Bug] "
labels: ["bug"]
assignees: []
body:
  - type: markdown
    attributes:
      value: Thanks for reporting a bug. Please fill out the template below.

  - type: dropdown
    id: component
    attributes:
      label: Affected Component
      description: Which layer or component is affected?
      options:
        - L1 Model Layer
        - L2 Capability Layer
        - L3 Collaboration Layer
        - L4 Governance Layer
        - Seven-Dimensional Evaluation Framework
        - Compliance Mapping
        - Documentation
        - Other
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: A clear description of the bug
      placeholder: What happened?
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Reproduction Steps
      description: Minimal code or commands to reproduce
      placeholder: |
        ```python
        from src.l4_governance import L4GovernanceLayer
        l4 = L4GovernanceLayer()
        ...
        ```
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What did you expect to happen?
    validations:
      required: true
