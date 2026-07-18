ANKA OS ROM - Redmi Note 9 (merlin) için Python 3 Gömülü Ortam
================================================================

Bu dizin (`python3/`) ROM içinde taşınan Python 3 çalışma ortamını içerir.
Termux veya herhangi bir üçüncü taraf uygulama gerektirmez.

Derleme sırasında GitHub Actions aşağıdaki adımları gerçekleştirir:
1. arm64 için Python 3 static binary indirir / çapraz derler
2. Sıkıştırılmış arşivi bu dizine açar
3. `bin/python3` çalıştırılabilir olarak yerleştirilir

Yerel geliştirme sırasında bu dizin boş bırakılabilir;
servis.sh Termux python3'e geri döner.
