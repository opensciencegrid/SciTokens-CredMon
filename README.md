# SciTokens-CredMon
SciTokens enabled CredMon for OSGConnect.

The CredMon is in charge of creating and renewing SciTokens on the submitter and 
worker node.  The CredMon has different behavior depending on whether it detects
it is running on a submitter or a execute node.

The CredMon detects whether it is running on the submitter or execute machine by testing
for the existance of the Private Key.  If the private key is found, the CredMon
assumes it is on the Submitter.  Otherwise, it is assumed to be on the execute node.

## Requirements

The SciTokens CredMon requires:
* The SciTokens package (RPM or [Python](https://pypi.python.org/pypi/scitokens) installation)
* The HTCondor-Python package

## Submitter Behavior

On the Submitter, the CredMon's primary responsibility is to convert the <username>.cred file into
a credential named <username>.cc.  In SciTokens' case, it creates a SciToken that is capable of writing
to the <username>'s stash directory.

An example SciToken payload is:

    {
      "scp": ["read:/user/dweitzel", "write:/user/dweitzel"],
      "sub": "dweitzel",
      "exp": 1505868419,
      "iat": 1505867219,
      "iss": "https://scitokens.org/osg-connect",
      "nbf": 1505867219
    }

The above example would allow access to read and write from the Stash repo.

Once the SciToken is created, along with it being written to the <username>.cc file,
the SciToken is also written to the <username>.cred.  The <username>.cred file is copied
to the worker node by the HTCondor Shadow to the HTCondor Starter.

## Execute Behavior

The CredMon only does 1 operation on the execute host, copy the <username>.cred to <username>.cc.
Since the Starter will copy the SciToken <username>.cred file to the execute node, just copy that to the credential.

## TODO: GlideinWMS Support

GlideinWMS may start as a 

