# Concurrent programming experiment with hyper simplistic "crowd" simulations

I want to learn more about concurrency and don't want to just play with trivial examples. So, this project is to
serve as a test bed for my concurrency experimentation.

This project allows dozens of `Bots` to move around the screen and collide with each other.  There are several kinds of
`Bots`, each with its own simple pre-programmed logic that defines how it moves about the screen.

The thought is to see how hard/easy it is to implement these different bots with different approaches to concurrency.
Some possibilities:

- step based simulation
- threads
- generators 
- asyncio
- Twisted
    - async
    - threads

In addition to running the simulation (letting the `Bots` run around), the app also provides keyboard controls to
interact with the simulation (pause time, advance frame by frame, add and remove bots, move bots, etc.) 


# Project Setup

    # Create venv
    py -3 -m venv venv
    source venv/Scripts/activate
    # Install dependencies
    pip install -r requirements.txt
    cd src/
    python -m crowd.crowd_sandbox

PyCharm

- Set `venv/` as project interpreter in PyCharm
- Mark `src/` directory as "sources root"
