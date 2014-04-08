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

# Pip packages

package { "psycopg2":
    provider => "pip",
    require => [Package["python-pip"],
                Package["python-dev"],
                Package["libpq-dev"]],
    ensure => present,
}

#package { "supervisor":
#    provider => "pip",
#    require => Package["python-pip"],
#    ensure => present,
#}

package { "django":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "django-extensions":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "south":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "jinja2":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "mimeparse":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "django-debug-toolbar":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "gunicorn":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "chainclient":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "pyzmq":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "docopt":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "coloredlogs":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}


# Set up DB schema and users

postgresql::server::role { 'chain':
    createdb => true,
    password_hash => postgresql_password('chain', 'LBWgC8AzqFzbrEY9swmsy6vYS'),
}

postgresql::server::db { 'chain':
    user     => 'chain',
    password => postgresql_password('chain', 'LBWgC8AzqFzbrEY9swmsy6vYS')
}
