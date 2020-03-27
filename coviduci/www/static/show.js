
$(document).ready(function() {
  $('#camas').DataTable({
    responsive: true,
    ajax: {
      url: '/data',
      data: function(d){
            console.log(d)
            return d
        },
    },
    columns: [
    {data: 'hospital'},
    {data: 'camas_total'},
    {data: 'camas_usadas'},
    ]
  });
  $('#personal').DataTable({
    responsive: true,
    ajax: {
      url: '/data',
      data: function(d){
            console.log(d)
            return d
        },
    },
    columns: [
    {data: 'hospital'},
    {data: 'medicos'},
    {data: 'enfermeros'},
    {data: 'auxiliares'},
    ]
  });
  $('#insumos').DataTable({
    responsive: true,
    ajax: {
      url: '/data',
      data: function(d){
            console.log(d)
            return d
        },
    },
    columns: [
    {data: 'hospital'},
    {data: 'respiradores'},
    {data: 'tubos_ett'},
    ]
  });
  $('#medicaciones').DataTable({
    responsive: true,
    ajax: {
      url: '/data',
      data: function(d){
            console.log(d)
            return d
        },
    },
    columns: [
    {data: 'hospital'},
    {data: 'primera'},
    {data: 'segunda'},
    ]
  });
  $('#pacientes').DataTable({
    responsive: true,
    ajax: {
      url: '/data',
      data: function(d){
            console.log(d)
            return d
        },
    },
    columns: [
    {data: 'hospital'},
    {data: 'ingresos'},
    {data: 'fallecidos'},
    ]
  });
});
