name: Feature Request
description: Propose a new feature for the four-layer architecture
title: "[Feature] "
labels: ["enhancement"]
body:
  - type: dropdown
    id: layer
    attributes:
      label: Affected Layer
      description: Which layer does the feature target?
      options:
        - L1 Model Layer
        - L2 Capability Layer
        - L3 Collaboration Layer
        - L4 Governance Layer
        - Cross-layer
        - Evaluation Framework
        - Compliance Mapping
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      description: What problem does this feature solve? Cite specific failure modes or use cases.
    validations:
      required: true

  - type: textarea
    id: proposal
    attributes:
      label: Proposed Implementation
      description: Sketch of the proposed implementation. Reference the relevant MAST failure mode if applicable.
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: What other approaches did you consider? Why this approach?
