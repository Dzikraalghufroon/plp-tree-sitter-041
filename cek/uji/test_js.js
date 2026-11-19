// TODO: hubungkan dengan socket io
function hitungTotalBelanja(keranjang) {
  let total = 0;
  // FIXME: hitung pajak PPN 11%
  for (let i = 0; i < keranjang.length; i++) {
    total += keranjang[i].harga;
  }
  return total;
}

// Fungsi panjang JS > 30 baris
function renderHalamanDashboard(data) {
  console.log("Render start");
  let html = "<div>";
  html += "<h1>Dashboard</h1>";
  html += "<p>Item 1</p>";
  html += "<p>Item 2</p>";
  html += "<p>Item 3</p>";
  html += "<p>Item 4</p>";
  html += "<p>Item 5</p>";
  html += "<p>Item 6</p>";
  html += "<p>Item 7</p>";
  html += "<p>Item 8</p>";
  html += "<p>Item 9</p>";
  html += "<p>Item 10</p>";
  html += "<p>Item 11</p>";
  html += "<p>Item 12</p>";
  html += "<p>Item 13</p>";
  html += "<p>Item 14</p>";
  html += "<p>Item 15</p>";
  html += "<p>Item 16</p>";
  html += "<p>Item 17</p>";
  html += "<p>Item 18</p>";
  html += "<p>Item 19</p>";
  html += "<p>Item 20</p>";
  html += "<p>Item 21</p>";
  html += "<p>Item 22</p>";
  html += "<p>Item 23</p>";
  html += "<p>Item 24</p>";
  html += "<p>Item 25</p>";
  html += "<p>Item 26</p>";
  html += "</div>";
  return html;
}
