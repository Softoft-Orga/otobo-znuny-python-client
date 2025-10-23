docker compose up -d --wait
docker compose exec web bash -c "rm -f Kernel/Config/Files/ZZZAAuto.pm ; bin/docker/quick_setup.pl --db-password 1234"