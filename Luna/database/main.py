import aiosqlite

from ..utils import Rank, Record, Bank
from ..secrets import Info


class Base:
    conn: aiosqlite.Connection

    def __init__(self, table_query: str) -> None:
        self.table_query = table_query

    async def setup(self) -> None:
        self.conn = await aiosqlite.connect(Info.DB_FILE)
        cursor = await self.conn.cursor()
        await cursor.execute(self.table_query)
        await self.conn.commit()
        await cursor.close()

    @property
    def connection(self) -> aiosqlite.Connection | None:
        return self.conn
    
    @connection.setter
    def connection(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn
    

class Experience(Base):
    conn: aiosqlite.Connection

    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS exps(user_id INTEGER, guild_id INTEGER, xp INTEGER, level INTEGER)")

    async def all_records(self) -> None | list[Rank]:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM exps")).fetchall()
        await cursor.close()
        return None if not data else [Rank(record[0], record[1], record[2], record[3]) for record in data]
    
    async def all_guild_records(self, guild_id: int) -> None | list[Rank]:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM exps WHERE guild_id = ?", (guild_id,))).fetchall()
        await cursor.close()
        return None if not data else [Rank(record[0], record[1], record[2], record[3]) for record in data]
    
    async def _raw_guild_records(self, guild_id: int) -> None | list:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM exps WHERE guild_id = ?", (guild_id,))).fetchall()
        await cursor.close()
        return data

    async def read(self, user_id: int, guild_id: int) -> None | Rank:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute('''SELECT * FROM exps WHERE user_id = ? AND guild_id = ?''', (user_id, guild_id,))).fetchone()
        await cursor.close()

        return None if record is None else Rank(record[0], record[1], record[2], record[3])

    async def create(self, user_id: int, guild_id: int, starting_xp: int=5, starting_level: int=1):
        if (check := await self.read(user_id, guild_id)):
            return check
        
        cursor = await self.conn.cursor()
        await cursor.execute('''INSERT INTO exps(user_id, guild_id, xp, level) VALUES(?, ?, ?, ?)''', (user_id, guild_id, starting_xp, starting_level,))
        await self.conn.commit()
        await cursor.close()
        return Rank(user_id, guild_id, starting_xp, starting_level)
        
    async def update(self, user_id: int, guild_id: int, *, xp: int=None, level: int=None) -> bool:
        if not xp and not level:
            return False
        
        cursor = await self.conn.cursor()

        if xp and not level:
            await cursor.execute("UPDATE exps SET xp = ? WHERE user_id = ? AND guild_id = ?", (xp, user_id, guild_id,))
            
        if level and not xp:
            await cursor.execute("UPDATE exps SET level = ? WHERE user_id = ? AND guild_id = ?", (level, user_id, guild_id,))
            
        if xp and level:
            await cursor.execute("UPDATE exps SET xp = ? , level = ? WHERE user_id = ? AND guild_id = ?",(xp,level,user_id, guild_id,))
        
        await self.conn.commit()
        await cursor.close()
        return True


class MessageDB(Base):
    conn: aiosqlite.Connection

    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS messages(user_id INTEGER, channel_id INTEGER, message_id INTEGER, guild_id INTEGER, dm_id INTEGER, dm_channel_id INTEGER)")


    async def read_user_message(self, user_id: int, message_id: int) -> None | Record:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM messages WHERE user_id = ? AND message_id = ?", (user_id, message_id,))).fetchone()
        if not record: return None
        return Record(record[2], record[0], record[3], record[1], record[4], record[5])

    async def read_message(self, message_id: int) -> None | list[Record]:
        cursor = await self.conn.cursor()
        records = await (await cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))).fetchall()
        if not records: return None
        return [Record(record[2], record[0], record[3], record[1], record[4], record[5]) for record in records]

    async def read_user(self, user_id: int) -> None | list[Record]:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM messages WHERE user_id = ?", (user_id,))).fetchall()
        if not record: return None
        return [Record(record[2], record[0], record[3], record[1], record[4], record[5]) for record in record]

    async def create(self, user_id: int, channel_id: int, message_id: int, guild_id: int, dm_id: int, dm_channel_id: int) -> bool | Record:
        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO messages(user_id, channel_id, message_id, guild_id, dm_id, dm_channel_id) VALUES(?, ?, ?, ?, ?, ?)", (user_id, channel_id, message_id, guild_id, dm_id, dm_channel_id,))
        await self.conn.commit()
        return Record(message_id, user_id, guild_id, channel_id, dm_id, dm_channel_id)
    
    async def remove(self, user_id: int, message_id: int) -> bool | Record:
        _check = await self.read_user_message(user_id, message_id)
        if _check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM messages WHERE user_id = ? AND message_id = ?", (_check.user_id, _check.message_id,))
        await self.conn.commit()
        return Record(_check.message_id, _check.user_id, _check.guild_id, _check.channel_id, _check.dm_id, _check.dm_channel_id)
    
    async def remove_user(self, user_id: int) -> bool:
        _check = await self.read_user(user_id)
        if _check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return True
    
    async def remove_message(self, message_id: int) -> bool:
        _check = await self.read_message(message_id)
        if _check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
        await self.conn.commit()
        return True

    
class Economy(Base):
    conn: aiosqlite.Connection

    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS mainbank(user_id INTEGER PRIMARY KEY, wallet INTEGER, bank INTEGER)")

    async def all_records(self) -> list[Bank] | None:
        cursor = await self.conn.cursor()
        all_records = await (await cursor.execute("SELECT * FROM mainbank")).fetchall() 
        if not all_records:
            return None
        return [Bank(record[0], record[1], record[2]) for record in all_records]

    
    async def read(self, user_id: int) -> Bank | None:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM mainbank WHERE user_id = ?", (user_id,))).fetchone()
        if not record:
            return None
        return Bank(record[0], record[1], record[2])

    async def create(self, user_id: int, wallet: int=500, bank: int=1000) -> Bank:
        if (record := await self.read(user_id)):
            return record
        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO mainbank(user_id, wallet, bank) VALUES(?, ?, ?)", (user_id, wallet, bank))
        await self.conn.commit()
        return Bank(user_id, wallet, bank)
    
    async def update(self, user_id: int, *, wallet: int=None, bank: int=None) -> bool:  
        if not wallet and not bank:
            return False
        cursor = await self.conn.cursor()
        if wallet and not bank:
            await cursor.execute("UPDATE mainbank SET wallet = ? WHERE user_id = ?", (wallet, user_id,))
        if bank and not wallet:
            await cursor.execute("UPDATE mainbank SET bank = ? WHERE user_id = ?", (bank, user_id,))
        if wallet and bank:
            await cursor.execute("UPDATE mainbank SET wallet = ?, bank = ? WHERE user_id = ?", (wallet, bank, user_id,))
        await self.conn.commit()
        return True
    
    async def delete(self, user_id: int) -> bool:
        if not await self.read(user_id):
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM mainbank WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return True


class DatabaseManager:
    ranks = Experience()
    messages = MessageDB()
    economy = Economy()

    async def setup(self) -> None:
        await self.ranks.setup()
        await self.messages.setup()
        await self.economy.setup()