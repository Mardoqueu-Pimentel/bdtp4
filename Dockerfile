FROM postgres

WORKDIR /bdtp4
COPY . .
RUN sudo pacman -Syu python-virtualenv
RUN createdb bdtp4
CMD source ./activate
