#!stateconf yaml . jinja

.python_packages:
  pkg.installed:
    - pkgs:
        {% for pkg in ["curl", "python-software-properties", "build-essential", "python", "python-dev", "python-setuptools"] %}
        - {{ pkg }}
        {% endfor %}

.pip:
  cmd:
    - run
    - name: 'curl -L https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python'
    - unless: 'test -f /usr/local/bin/pip'
    - reload_modules: true
    - require:
      - pkg: .python_packages

.distribute:
  pip:
    - installed
    - name: distribute>=0.7.3
    - require:
      - cmd: .pip

.virtualenv:
  pip:
    - installed
    - name: virtualenv
    - require:
      - cmd: .pip

.virtualenvwrapper:
  pip:
    - installed
    - name: virtualenvwrapper
    - require:
      - pip: .virtualenv

.virtualenv_wrapper.sh:
  file:
    - managed
    - name: /home/vagrant/.bash.after.d/virtualenv_wrapper.sh
    - user: vagrant
    - group: vagrant
    - mode: 0770
    - source: salt://bash/virtualenv_wrapper.sh.jinja
    - template: jinja
    - defaults:
        virtualenv_home: /home/vagrant/.virtualenvs/
    - require:
      - file: bash::bash.after.d
      - pip: .virtualenvwrapper

.create_venv:
  virtualenv.managed:
    - name: /home/vagrant/.virtualenvs/kim
    - mode: 775
    - require:
      - file: .virtualenv_wrapper.sh
    - runas: vagrant
