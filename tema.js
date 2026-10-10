/* =====================================================================
   tema.js - Aplica el tema visual guardado y agrega el panel de
   "Configuración visual" abajo a la izquierda. Se carga en el <head>
   de cada página (sin defer) para que no haya parpadeo de colores.
   ===================================================================== */
(function () {
  const TEMAS = [
    { id: 'oscuro',    nombre: 'Oscuro',    fondo: '#1d2042', panel: '#30356a', lado: '#20234a', barras: ['#22d3ee', '#fbbf24', '#fb7185'] },
    { id: 'claro',     nombre: 'Claro',     fondo: '#eef0fa', panel: '#ffffff', lado: '#ffffff', barras: ['#2563eb', '#ea580c', '#be123c'] },
    { id: 'esmeralda', nombre: 'Esmeralda', fondo: '#f4f1ec', panel: '#ffffff', lado: '#1f5c4a', barras: ['#2563eb', '#d97706', '#b91c1c'] },
    { id: 'oceano',    nombre: 'Océano',    fondo: '#0a1828', panel: '#15314f', lado: '#0c1d31', barras: ['#a78bfa', '#fcd34d', '#fb7185'] },
  ];
  const CLAVE = 'ti_tema';
  const DEFECTO = 'oscuro';

  function leer() {
    try { const t = localStorage.getItem(CLAVE); if (TEMAS.some(x => x.id === t)) return t; } catch {}
    return DEFECTO;
  }
  function aplicar(id) {
    document.documentElement.dataset.tema = id;
    try { localStorage.setItem(CLAVE, id); } catch {}
    document.querySelectorAll('.temas button').forEach(b => b.classList.toggle('on', b.dataset.tema === id));
    const t = TEMAS.find(x => x.id === id);
    document.querySelectorAll('.muestra-actual').forEach(m =>
      m.style.background = `linear-gradient(90deg, ${t.barras.join(', ')})`);
    window.dispatchEvent(new CustomEvent('tema-cambiado', { detail: id }));
  }
  document.documentElement.dataset.tema = leer();   // antes de pintar la página

  // Magnitud de un valor respecto al máximo: baja, media o alta (para el color de las barras)
  function magnitud(valor, maximo) {
    const r = maximo > 0 ? Number(valor) / maximo : 0;
    return r < 0.34 ? 'mag-baja' : r < 0.67 ? 'mag-media' : 'mag-alta';
  }
  function leyenda(textos = ['Bajo', 'Medio', 'Alto']) {
    return `<div class="leyenda-mag"><span><i class="l-baja"></i>${textos[0]}</span>`
      + `<span><i class="l-media"></i>${textos[1]}</span><span><i class="l-alta"></i>${textos[2]}</span></div>`;
  }

  window.TemaVisual = { TEMAS, actual: leer, aplicar, magnitud, leyenda };

  const ICONO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r="1.5"/><circle cx="17.5" cy="10.5" r="1.5"/><circle cx="8.5" cy="7.5" r="1.5"/><circle cx="6.5" cy="12.5" r="1.5"/><path d="M12 2a10 10 0 1 0 0 20c.9 0 1.6-.7 1.6-1.6 0-.4-.2-.8-.4-1.1-.3-.3-.4-.7-.4-1.1 0-.9.7-1.6 1.6-1.6H16a6 6 0 0 0 6-6c0-4.9-4.5-8.6-10-8.6z"/></svg>';

  function crearPanel() {
    const cont = document.createElement('div');
    cont.className = 'config-visual';
    cont.innerHTML = `
      <button type="button" aria-haspopup="true" aria-expanded="false">${ICONO}<span class="txt">Configuración visual</span><i class="muestra-actual"></i></button>
      <div class="config-pop" role="dialog" aria-label="Configuración visual" hidden>
        <h4>Configuración visual</h4>
        <p>Elige el aspecto. Se aplica en todas las páginas y en los PDF.</p>
        <div class="temas">${TEMAS.map(t => `
          <button type="button" data-tema="${t.id}">
            <span class="vista" style="background:${t.fondo}">
              <span style="background:${t.lado}"></span>
              <span>${t.barras.map((c, i) => `<i style="background:${c};height:${[45, 75, 100][i]}%"></i>`).join('')}</span>
            </span>${t.nombre}
          </button>`).join('')}
        </div>
      </div>`;
    const boton = cont.querySelector('button');
    const pop = cont.querySelector('.config-pop');
    const abrir = v => { pop.hidden = !v; boton.setAttribute('aria-expanded', String(v)); };
    boton.addEventListener('click', e => { e.stopPropagation(); abrir(pop.hidden); });
    pop.addEventListener('click', e => {
      e.stopPropagation();
      const b = e.target.closest('[data-tema]');
      if (b) aplicar(b.dataset.tema);
    });
    document.addEventListener('click', () => abrir(false));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') abrir(false); });
    return cont;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const panel = crearPanel();
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      const usuario = sidebar.querySelector('.user');
      sidebar.insertBefore(panel, usuario || null);
      if (usuario) usuario.style.marginTop = '0';
      panel.style.marginTop = 'auto';
    } else {
      panel.classList.add('config-flotante');     // páginas sin barra lateral (login)
      document.body.appendChild(panel);
    }
    aplicar(leer());
  });
})();
