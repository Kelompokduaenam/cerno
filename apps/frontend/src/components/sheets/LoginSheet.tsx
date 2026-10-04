import { useState } from "react";
import type { FormEvent } from "react";
import Sheet from "../Sheet";
import { Button } from "../Button";

type FieldErrors = Partial<Record<"name" | "email" | "password", string>>;

export default function LoginSheet({ onClose }: { onClose: () => void }) {
  const [register, setRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<FieldErrors>({});
  const [notice, setNotice] = useState("");

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const next: FieldErrors = {};
    if (register && !name.trim()) next.name = "Masukkan nama Anda.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) next.email = "Masukkan alamat email yang valid.";
    if (password.length < 8) next.password = "Kata sandi minimal 8 karakter.";
    setErrors(next);
    setNotice(Object.keys(next).length === 0 ? `Formulir ${register ? "pendaftaran" : "masuk"} sudah valid. Ini masih simulasi; akun belum ${register ? "dibuat" : "dimasuki"}.` : "Periksa kembali bagian yang ditandai.");
  };
  const switchMode = () => { setRegister(!register); setErrors({}); setNotice(""); };

  return <Sheet title={register ? "Buat akun CERNO" : "Masuk ke CERNO"} eyebrow="Simulasi formulir" onClose={onClose}>
    <div className="auth-intro"><span className="mini-mark">C</span><p>Isi formulir untuk mencoba alur. Data belum dikirim atau disimpan.</p></div>
    <form onSubmit={submit} noValidate>
      {register && <><label className="field-label" htmlFor="name">Nama</label><input id="name" className="field" autoComplete="name" value={name} onChange={(e) => { setName(e.target.value); setErrors({ ...errors, name: undefined }); }} aria-invalid={!!errors.name} aria-describedby={errors.name ? "name-error" : undefined} />{errors.name && <p className="field-error" id="name-error">{errors.name}</p>}</>}
      <label className="field-label" htmlFor="email">Email</label><input id="email" type="email" className="field" autoComplete="email" value={email} onChange={(e) => { setEmail(e.target.value); setErrors({ ...errors, email: undefined }); }} aria-invalid={!!errors.email} aria-describedby={errors.email ? "email-error" : undefined} placeholder="nama@email.com" />{errors.email && <p className="field-error" id="email-error">{errors.email}</p>}
      <label className="field-label" htmlFor="password">Kata sandi</label><input id="password" type="password" className="field" autoComplete={register ? "new-password" : "current-password"} value={password} onChange={(e) => { setPassword(e.target.value); setErrors({ ...errors, password: undefined }); }} aria-invalid={!!errors.password} aria-describedby={errors.password ? "password-error" : undefined} placeholder="Minimal 8 karakter" />{errors.password && <p className="field-error" id="password-error">{errors.password}</p>}
      {notice && <p className={Object.keys(errors).length ? "form-notice form-notice--error" : "form-notice"} role="status">{notice}</p>}
      <Button type="submit" className="button--full">{register ? "Periksa formulir daftar →" : "Periksa formulir masuk →"}</Button>
    </form>
    <p className="auth-switch">{register ? "Sudah punya akun?" : "Belum punya akun?"} <button onClick={switchMode}>{register ? "Masuk" : "Daftar"}</button></p>
  </Sheet>;
}
