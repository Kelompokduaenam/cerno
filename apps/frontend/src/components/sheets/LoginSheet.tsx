import { useState } from "react";
import Sheet from "../Sheet";
import { Button } from "../Button";

export default function LoginSheet({ onClose }: { onClose: () => void }) {
  const [register, setRegister] = useState(false);
  return <Sheet title={register ? "Buat akun CERNO" : "Masuk ke CERNO"} eyebrow="Simpan dengan aman" onClose={onClose}>
    <div className="auth-intro"><span className="mini-mark">C</span><p>Riwayat tersimpan dalam bentuk tersamarkan. CERNO tidak menjual data Anda.</p></div>
    {register && <><label className="field-label" htmlFor="name">Nama</label><input id="name" className="field" placeholder="Nama Anda" /></>}
    <label className="field-label" htmlFor="email">Email</label><input id="email" type="email" className="field" placeholder="nama@email.com" />
    <label className="field-label" htmlFor="password">Kata sandi</label><input id="password" type="password" className="field" placeholder="Minimal 8 karakter" />
    <Button className="button--full">{register ? "Daftar →" : "Masuk →"}</Button>
    <p className="auth-switch">{register ? "Sudah punya akun?" : "Belum punya akun?"} <button onClick={() => setRegister(!register)}>{register ? "Masuk" : "Daftar"}</button></p>
  </Sheet>;
}
