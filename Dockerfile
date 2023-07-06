FROM python as builder

WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user --requirement requirements.txt

FROM python
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT python bot.py ${BUSTERBOT_TOKEN} ${REDIS_HOST}

