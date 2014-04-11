class { 'postgresql::server': }

#exec { "apt-update":
#    command => "apt-get update",
#    path => "/usr/bin",
#}

# Installed Packages

package { "python-dev":
    ensure  => present,
#    require => Exec["apt-update"],
}

package { "libpq-dev":
    ensure  => present,
#    require => Exec["apt-update"],
}

package { "python-pip":
    ensure  => present,
#    require => Exec["apt-update"],
}

package { "nginx":
    ensure  => present,
#    require => Exec["apt-update"],
}

package { "supervisor":
    ensure  => present,
#    require => Exec["apt-update"],
}

# python dependencies are listed in setup.py

# Set up DB schema and users

postgresql::server::role { 'chain':
    createdb => true,
    password_hash => postgresql_password('chain', 'secret'),
}

postgresql::server::db { 'chain':
    user     => 'chain',
    password => postgresql_password('chain', 'secret')
}
