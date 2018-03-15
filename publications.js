var options = {
  valueNames: [ 'name', 'born' ],
  item: '<li><h3 class="name"></h3><p class="born"></p></li>'
};

var values = [{
    name: 'Jonny Strömberg',
    born: 1986
  },
  {
    name: 'Jonas Arnklint',
    born: 1985
  },
  {
    name: 'Martina Elm',
    born: 1986
}];

var userList = new List('users', options, values);

userList.add({
  name: "Gustaf Lindqvist",
  born: 1983
});
