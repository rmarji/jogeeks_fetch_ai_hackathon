graph TD
    A[Price Agent] -->|Price Data| B[Analysis Agent]
    B -->|Analysis Results| C[Alert Agent]
    C -->|Notifications| D[User Agent]
    D -->|Alert Configurations| C
    D -->|Cryptocurrency Preferences| A
    E[External API] -->|Market Data| A
    
    subgraph Protocols
    F[Price Data Protocol]
    G[Analysis Protocol]
    H[Alerts Protocol]
    end
    
    style A fill:#f9d77e,stroke:#f9b93e,stroke-width:2px
    style B fill:#a1d4c6,stroke:#5aaa95,stroke-width:2px
    style C fill:#f4a7a1,stroke:#e86a60,stroke-width:2px
    style D fill:#a7c7f4,stroke:#6a95e8,stroke-width:2px