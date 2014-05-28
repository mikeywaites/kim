#!stateconf yaml . jinja

.bash.before.d:
  file:
    - directory
    - name: /home/vagrant/.bash.before.d
    - user: vagrant
    - group: vagrant
    - mode: 0770

.bash.after.d:
  file:
    - directory
    - name: /home/vagrant/.bash.after.d
    - user: vagrant
    - group: vagrant
    - mode: 0770

.bashrc:
  file:
    - managed
    - name: /home/vagrant/.bashrc
    - user: vagrant
    - group: vagrant
    - mode: 0770
    - source: salt://bash/.bashrc.jinja
    - template: jinja
    - defaults:
        before_path: /home/vagrant/.bash.before.d
        after_path: /home/vagrant/.bash.after.d
