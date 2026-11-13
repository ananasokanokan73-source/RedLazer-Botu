{ Client, GatewayIntentBits, EmbedBuilder, PermissionsBitField } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers
  ]
});

const PREFIX = "!"; // Komut öneki

client.once('ready', () => {
  console.log(`[+] Bot aktif! Giriş yapıldı: ${client.user.tag}`);
  client.user.setActivity('!yardım yazarak komutları görebilirsin', { type: 3 }); // 3 = Watching
});

// Üye sunucuya katıldığında hoş geldin mesajı
client.on('guildMemberAdd', member => {
  const channel = member.guild.systemChannel;
  if (!channel) return;

  const embed = new EmbedBuilder()
    .setColor('#00FF00')
    .setTitle('Sunucuya Biri Katıldı!')
    .setDescription(`Aramıza hoş geldin, ${member}! Seninle beraber **${member.guild.memberCount}** kişi olduk. 🎉`)
    .setTimestamp();

  channel.send({ embeds: [embed] });
});

client.on('messageCreate', async message => {
  if (message.author.bot || !message.guild) return;

  // Sadece prefix ile başlayan mesajları işle
  if (!message.content.startsWith(PREFIX)) return;

  const args = message.content.slice(PREFIX.length).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  // 1. YARDIM MENÜSÜ
  if (command === 'yardım') {
    const embed = new EmbedBuilder()
      .setColor('#5865F2')
      .setTitle('🤖 Bot Komut Listesi')
      .setDescription('Aşağıdan tüm komutları ve ne işe yaradıklarını görebilirsin:')
      .addFields(
        { name: '🏓 `!ping`', value: 'Botun gecikme süresini (ms) gösterir.', inline: false },
        { name: '👤 `!profil`', value: 'Kendi profil bilgilerini veya etiketlediğin kişinin bilgilerini gösterir.', inline: false },
        { name: '🗑️ `!temizle [sayı]`', value: 'Belirtilen miktarda mesajı siler (Moderatörler içindir).', inline: false },
        { name: '🔨 `!ban [@kullanıcı]`', value: 'Etiketlenen kullanıcıyı sunucudan yasaklar (Yönetici yetkisi ister).', inline: false },
        { name: '🎲 `!zar`', value: '1 ile 6 arasında rastgele bir zar atar.', inline: false },
        { name: '⏰ `!saat`', value: 'Şu anki güncel saati gösterir.', inline: false }
      )
      .setFooter({ text: 'Gelişmiş Bot Sistemi' })
      .setTimestamp();

    message.reply({ embeds: [embed] });
  }

  // 2. PİNG
  else if (command === 'ping') {
    const sent = await message.reply('Hesaplanıyor...');
    const ping = sent.createdTimestamp - message.createdTimestamp;
    sent.edit(`Pong! 🏓 Gecikme: **${ping}ms** | WebSocket: **${client.ws.ping}ms**`);
  }

  // 3. PROFİL BİLGİSİ
  else if (command === 'profil') {
    const target = message.mentions.users.first() || message.author;
    const member = message.guild.members.cache.get(target.id);

    const embed = new EmbedBuilder()
      .setColor('#FF0055')
      .setTitle(`${target.username} - Kullanıcı Profili`)
      .setThumbnail(target.displayAvatarURL({ dynamic: true }))
      .addFields(
        { name: 'Kullanıcı Adı', value: target.tag, inline: true },
        { name: 'ID', value: target.id, inline: true },
        { name: 'Sunucuya Katılım', value: `<t:${Math.floor(member.joinedTimestamp / 1000)}:R>`, inline: false }
      )
      .setTimestamp();

    message.reply({ embeds: [embed] });
  }

  // 4. MESAJ TEMİZLEME (Moderatör)
  else if (command === 'temizle') {
    if (!message.member.permissions.has(PermissionsBitField.Flags.ManageMessages)) {
      return message.reply('❌ Bu komutu kullanmak için **Mesajları Yönet** yetkisine sahip olmalısın.');
    }

    const count = parseInt(args[0]);
    if (!count || count < 1 || count > 100) {
      return message.reply('⚠️ Lütfen 1 ile 100 arasında silinecek mesaj miktarı belirt! Örnek: `!temizle 10`');
    }

    try {
      await message.channel.bulkDelete(count, true);
      const msg = await message.channel.send(`🧹 Başarıyla **${count}** adet mesaj silindi.`);
      setTimeout(() => msg.delete(), 3000); // 3 saniye sonra bildirim mesajını da sil
    } catch (error) {
      console.error(error);
      message.reply('❌ Mesajlar silinirken bir hata oluştu (14 günden eski mesajlar toplu silinemez).');
    }
  }

  // 5. BAN ATMA (Yönetici)
  else if (command === 'ban') {
    if (!message.member.permissions.has(PermissionsBitField.Flags.BanMembers)) {
      return message.reply('❌ Bu komutu kullanmak için **Üyeleri Yasakla** yetkisine sahip olmalısın.');
    }

    const target = message.mentions.members.first();
    if (!target) {
      return message.reply('⚠️ Lütfen yasaklanacak kullanıcıyı etiketle! Örnek: `!ban @kullanici`');
    }

    if (!target.bannable) {
      return message.reply('❌ Bu kullanıcıyı banlayamam çünkü yetkisi benden üstün veya aynı seviyede.');
    }

    await target.ban();
    message.channel.send(`🔨 **${target.user.tag}** sunucudan başarıyla yasaklandı!`);
  }

  // 6. ZAR ATMA
  else if (command === 'zar') {
    const result = Math.floor(Math.random() * 6) + 1;
    message.reply(`🎲 Attığın zar: **${result}**`);
  }

  // 7. SAAT GÖSTERME
  else if (command === 'saat') {
    const time = new Date().toLocaleTimeString('tr-TR', { timeZone: 'Europe/Istanbul' });
    message.reply(`🕒 Türkiye Saati ile şu an: **${time}**`);
  }
});

// Bot token'ı ile giriş yap
client.login("BURAYA_BOTUNUN_TOKENINI_YAZ");
