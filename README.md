Doppel2 Server Setup Instructions
=================================

Install puppet and the proper puppet modules with

    sudo apt-get install puppet
    sudo puppet module install puppetlabs/postgresql

Then set up the server with

    sudo puppet apply manifest.pp
