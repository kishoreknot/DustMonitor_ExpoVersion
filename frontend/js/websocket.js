let socket = null;

export async function startSensorStream(config = {}, onData) {

  if (socket) {
    socket.close();
    socket = null;
  }
  
  socket = new WebSocket(`ws://${location.host}/ws/sensor`);

  socket.onopen = () => {
    socket.send(JSON.stringify({
      continuous : Boolean(config.continuous),
      period_in_seconds: config.period,
      network_address: config.networkAddress
    }));
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onData(data);

    // Auto-close after first response (single-shot)
    // if (options.closeAfterFirstResponse) {
    //   socket.close();
    //   socket = null;
    // }
  };

  socket.onerror = (err) => {
    console.error("WebSocket error", err);
  };
}

export function stopSensorStream() {
  if (socket) {
    socket.close();
    socket = null;
  }
}
