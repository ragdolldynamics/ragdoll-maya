Quick sanity check for overlapping shapes and an initial state residing within limits.

- Turn off gravity. Nothing should move when you play.
    - If something *does* move..
        - Disable collisions on everything
        - If something still *does* move..
            1. Disable all limits and guides
            2. Enable limits one-by-one
        - If something now *does not* move..
            1. Everything is OK
    - If something *does not* move..
        1. Everything is OK
