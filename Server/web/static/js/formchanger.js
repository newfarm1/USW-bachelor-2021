function radioChange(variable)
{
    if (variable ==='dict')
    {
        document.getElementById("mask_toggle").classList.add("hide");
        document.getElementById("dict").classList.remove("hide");
        document.getElementById("brute_toggle").classList.remove("hide");
        document.getElementById("costum_length").classList.remove("hide");
        document.getElementById("len1").placeholder='Default lenght is 10000 words';
        document.getElementById("len2").classList.add("hide");
    }

  if (variable ==='mask')
  {
      document.getElementById("mask_toggle").classList.remove("hide");
      document.getElementById("dict").classList.add("hide");
      document.getElementById("brute_toggle").classList.add("hide");
      document.getElementById("costum_length").classList.add("hide");
  
  }

  if (variable ==='brute')
  {
      document.getElementById("mask_toggle").classList.add("hide");
      document.getElementById("dict").classList.add("hide");
      document.getElementById("brute_toggle").classList.remove("hide");
      document.getElementById("costum_length").classList.remove("hide");
      document.getElementById("len1").placeholder='Default lenght start is 8 characters';
      document.getElementById("len2").classList.remove("hide");
  }
}

function radioChange2(variable)
{
  if (variable ==='open')
  {
      document.getElementById("len1").removeAttribute("disabled", "");
      document.getElementById("len2").removeAttribute("disabled", "");

  
  }
  if (variable ==='close')
  {
      document.getElementById("len1").setAttribute("disabled", "");
      document.getElementById("len2").setAttribute("disabled", "");

  }
}