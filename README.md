# Rarity bot v1.1

___________________________________________________

**CAREFUL USE THIS SOFTWARE AT YOUR OWN RISKS**

_____________________________________________________


This bot will automatically:

- Level up every summoner in an address who is ready for it
- Claim gold for every summoner ready for it
- Make your summoners go into an adventure
- Farm The Cellar dungeon if there is loot to claim for each summoner

## Installation

You need python and pip3 installed on your host. 

- on Mac you need typically need to install Xcode.
- on Windows you need to install Visual Studio build tools (C++ build tools) [https://www.youtube.com/watch?v=_keTL9ymGjw](https://www.youtube.com/watch?v=_keTL9ymGjw)
-- on Linux python3 is already installed on most distros.

Before running the code you'll need to install a few dependencies with:

```powershell
pip3 install --user web3 colorama argparse getpass
```

Next, clone the repository or simply download the files. Now you can run `rarity.py`!

## First time run

Before you can run the bot, you need to import a private key to your account. We advise that you select a private key from a dedicated account for rarity you already created on metamask.

**A PRIVATE KEY IS DIFFERENT FROM A SEED, DON'T ENTER YOUR SEED ON THIS PROGRAM**

On Metamask you can access your private key from the "Account details" panel.

Open a shell in the directory of `rarity.py` and run:

```
python3 rarity.py run --import-key
```

This will store the private key you paste in an encrypted file `privatekeyencrypted.json` located in the active directory. You'll have to choose a password for that and use this password again every time you run the script.

## Running the script

To run the program, simply open a shell at the location of `rarity.py` and run:

```
python3 rarity.py run
```

You're supposed to run this script once a day but the script won't take any actions if there is nothing to do.

## Other commands

Beyond "run", the bot can also perform other commands:

- "run" to run actions (by default, adenture, level up, etc). The actions are configurable with `--actions`
- "list" to simply list the summoners
- "check_gas" to print the price in FTM of common actions
- "summon" to create new summoners. Requires the additional argument `--class`.

Examples:

```
# Free and doesn't require password
python3 rarity.py list
python3 rarity.py check_gas

# Run full daiy routine
python3 rarity.py run
# Run full daiy routine in batch mode (faster)
python3 rarity.py run --txmode batch
# Run only adventure and cellar
python3 rarity.py run --actions adventure cellar

# Create 1 Bard
python3 rarity.py summon --class Bard
# Create 2 Fighters
python3 rarity.py summon --class Fighter -n 2
# Create 3 Barbarians (class ID 1) in batched tx (faster)
python3 rarity.py summon --class 1 -n 3 --txmode batch
```


## Advanced

The rarity bot can take a number of optional arguments. Run `python3 rarity.py --help` for an up-to-date documentation.

```
usage: rarity.py [-h] [-k KEYFILE] [-p PASSWORD] [--import-key] [--txmode TXMODE]
                 [-a [ACTIONS [ACTIONS ...]]] [--class SUMMONER_CLASS] [-n COUNT]
                 {run,list,summon,check_gas}

Manage your rarity summoners

positional arguments:
  {run,list,summon,check_gas}
                        Main command: "run" to run the bot (configure with --actions), "list"
                        to simply list summoners, "summon" to create new summoners (configure
                        with -n and --class) "check_gas" to show price in FTM of common
                        actions,

optional arguments:
  -h, --help            show this help message and exit
  -k KEYFILE, --keyfile KEYFILE
                        Path to encrypted keyfile
  -p PASSWORD, --password PASSWORD
                        Password to decrypt the keyfile. Be aware it will be available in
                        plaintext in the shell history. Use of interactive login is
                        preferable if possible.
  --import-key          Import a private key which will be stored encrypted in
                        `privatekeyencrypted.json`
  --txmode TXMODE       How transactions are processed. "legacy" to send them one by one and
                        wait for the receipt each time. "batch" to send tx in batches and
                        wait less often
  -a [ACTIONS [ACTIONS ...]], --actions [ACTIONS [ACTIONS ...]]
                        All actions to take. Will do everything by default. Select one or
                        more from "list" (list Summoners on address), "adventure",
                        "level_up", "claim_gold", "cellar" (send to cellar dungeon)
  --class SUMMONER_CLASS
                        Class used for summoning. Required if command is "summon". Can be
                        class ID (1 to 11) or class name (e.g. "Bard").
  -n COUNT, --count COUNT
                        Number of summoners to create if command is "summon". Default is 1
```


If your private key is not in the same directory (or if it is not called `privatekeyencrypted.json`), you can provide an alternative keyfile with the `--keyfile KEYFILE`. This allows you to maintain summoners on several addresses.

```
python3 rarity.py run --keyfile key1.json
python3 rarity.py run --keyfile key2.json
```

To run the bot in a non-interactive setting (e.g. a cron job), you can use `--password "PWD"` to pass the password and skip the interactive login. 
Note this is not recommended unless you know what you're doing, as the password will then be available in plaintext in the shell history. 
One way to avoid that is to use an environment variable and call `python3 rarity.py run --keyfile /path/to/key.json --password "$KEY_PWD"`.

## Using --actions to customise the run

You can control the actions taken by the bot runs on a very granular level using `--actions action1 action2 etc`. 
This is only available if the main command is "run".
The available actions are:

- "list": Print the list of summoners
- "adventure": Send summoners on adventure (when possible)
- "level_up": Level up summoners who can
- "claim_gold": Claim gold for summoners who can
- "cellar": Send summoners to the Cellar dungeon (when expected loot > 0)


## Warning about fees

There is no hard cap for gas price. Currently, the script ask the gas price to the web3 provider, **if fees are very high when you run the script, it will not warn you**.

*By Olocrom & Asa*

Tips some FTM (on the phantom network) if you liked this 🙂 : 0x128bd256da23c382D3D27a46FEAf32212154f159