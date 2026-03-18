flowchart TD
    A([Start]) --> B[Load songs from CSV]
    B --> C[Load user taste profile]
    C --> D[Pick next song]

    D --> E{Genre match?}
    E -- Yes --> F[+2 pts]
    E -- No --> G[+0 pts]

    F --> H{Mood match?}
    G --> H

    H -- Yes --> I[+2 pts]
    H -- No --> J[+0 pts]

    I --> K[Score numeric features]
    J --> K

    K --> K1["energy gap → pts"]
    K --> K2["valence gap → pts"]
    K --> K3["danceability gap → pts"]
    K --> K4["acousticness gap → pts"]
    K --> K5["tempo gap → pts"]

    K1 --> L[Sum all points → final score]
    K2 --> L
    K3 --> L
    K4 --> L
    K5 --> L

    L --> M{More songs?}
    M -- Yes --> D
    M -- No --> N[Sort songs by score descending]
    N --> O[Return top K results]
    O --> P([End])