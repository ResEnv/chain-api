include postgresql::server

exec { "apt-update":
    command => "apt-get update",
    path => "/usr/bin",
}

# Installed Packages

package { "python-dev":
    ensure  => present,
    require => Exec["apt-update"],
}

#package { "libxml2-dev":
#    ensure  => present,
#    require => Exec["apt-update"],
#}
#
#package { "libxslt-dev":
#    ensure  => present,
#    require => Exec["apt-update"],
#}

package { "libpq-dev":
    ensure  => present,
    require => Exec["apt-update"],
}

package { "postgresql":
    ensure  => present,
    require => Exec["apt-update"],
}

package { "python-pip":
    ensure  => present,
    require => Exec["apt-update"],
}

# Pip packages

package { "psycopg2":
    provider => "pip",
    require => [Package["python-pip"],
                Package["python-dev"],
                Package["libpq-dev"]],
    ensure => present,
}

package { "supervisor":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "django":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "south":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "djangorestframework":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "markdown":
    provider => "pip",
    require => Package["python-pip"],
    ensure => present,
}

package { "django-filter":
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


# Running Services

#service { "postgresql":
#    ensure  => "running",
#    require => Package["postgresql"],
#}

# Set up DB schema and users

postgresql::database_user { 'doppellab':
    # enable createdb permissions so django can create test DBs
    createdb => true
}

postgresql::db { 'doppellab':
  user     => 'doppellab',
  password => 'secret'
}
