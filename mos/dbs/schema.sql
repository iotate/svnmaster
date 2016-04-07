/** 用户表 **/
drop table if exists users;
create table users (
    id integer primary key autoincrement,
    fullname text not null ,
    username text not null unique,
    password text not null,
    email text not null,
	comments text,
    is_admin integer not null,
	is_active integer not null,
	lasttime text
);
insert into users('fullname','username','password','email','comments','is_admin','is_active','lasttime') values('所有用户','*','idonotknowyoudonotknowalso','all@iota.com','我代表所有用户','0','1','2012-03-31 20:58:40');
insert into users('fullname','username','password','email','comments','is_admin','is_active','lasttime') values('管理员','admin','admin','admin@iota.com','我是超级用户','1','1','2012-03-31 20:58:40');
insert into users('fullname','username','password','email','comments','is_admin','is_active','lasttime') values('大师','svnmaster','svnmaster','binnacler@iota.com','我是大师','1','1','2012-03-31 20:58:40');

/** 用户组表 **/
drop table if exists groups;
create table groups (
    id integer primary key autoincrement,
    groupname text not null unique,
	comments text,
	is_active integer not null,
    lasttime text
	
);
insert into groups('groupname','comments','is_active','lasttime') values('G-ADMIN','G开头 代表普通组','1','2012-03-31 20:58:40');
insert into groups('groupname','comments','is_active','lasttime') values('D-RD','D开头 代表部门组','1','2012-03-31 20:58:40');
insert into groups('groupname','comments','is_active','lasttime') values('P-MOS','P开头 代表产品或项目组','1','2012-03-31 20:58:40');

/** 用户-用户组对应表 **/
drop table if exists uig;
create table uig (
    id integer primary key autoincrement,
    group_id integer not null,
	user_id integer not null,
    lasttime text
	
);
insert into uig('group_id','user_id','lasttime') values('1','2','2012-03-31 20:58:40');
insert into uig('group_id','user_id','lasttime') values('1','3','2012-03-31 20:58:40');
insert into uig('group_id','user_id','lasttime') values('3','3','2012-03-31 20:58:40');

/** 配置库表 **/
drop table if exists repos;
create table repos (
    id integer primary key autoincrement,
    reponame text not null unique,
	comments text,
	is_active integer not null,
	lasttime text
);
insert into repos('reponame','comments','is_active','lasttime') values('mos','MOS产品配置库','1','2012-03-31 20:58:40');
insert into repos('reponame','comments','is_active','lasttime') values('svnmaster','svnmaster库','1','2012-03-31 20:58:40');

/** 配置库权限项表 **/
drop table if exists auth_items;
create table auth_items (
    id integer primary key autoincrement,
    repo_id integer not null ,
    authitem text not null
);
insert into auth_items('repo_id','authitem') values('1','/');
insert into auth_items('repo_id','authitem') values('2','/');
insert into auth_items('repo_id','authitem') values('1','/codes');
insert into auth_items('repo_id','authitem') values('1','/docs');
insert into auth_items('repo_id','authitem') values('2','/docs');

/** 配置库-用户-权限表 **/
drop table if exists auth_users;
create table auth_users (
    id integer primary key autoincrement,
    authitem_id integer not null ,
    user_id integer not null ,
	authtype text not null,
	lasttime text
);
insert into auth_users('authitem_id','user_id','authtype','lasttime') values('1','2','读写','2012-03-31 20:58:40');
insert into auth_users('authitem_id','user_id','authtype','lasttime') values('2','3','禁止','2012-03-31 20:58:40');
insert into auth_users('authitem_id','user_id','authtype','lasttime') values('3','3','禁止','2012-03-31 20:58:40');

/** 配置库-用户组-权限表 **/
drop table if exists auth_groups;
create table auth_groups (
    id integer primary key autoincrement,
    authitem_id integer not null ,
    group_id integer not null ,
	authtype text not null,
	lasttime text
);
insert into auth_groups('authitem_id','group_id','authtype','lasttime') values('1','1','读写','2012-03-31 20:58:40');
insert into auth_groups('authitem_id','group_id','authtype','lasttime') values('2','1','只读','2012-03-31 20:58:40');
insert into auth_groups('authitem_id','group_id','authtype','lasttime') values('2','1','禁止','2012-03-31 20:58:40');

/** 查询组中的用户名 
select users.id as userid,fullname,username FROM users CROSS JOIN uig where users.id = uig.user_id and uig.group_id = '1' order by username;
查询用户所在的组
select groups.id as groupid,groupname FROM groups CROSS JOIN uig where groups.id = uig.group_id and uig.user_id = '1' order by groupname;
**/

/** 查询配置库的配置项 
select reponame,authitem FROM auth_items CROSS JOIN repos where auth_items.repo_id = repos.id order by reponame,authitem;
查询配置库中配置项对应的用户
select reponame,authitem,fullname,username,authtype from auth_users cross join users,repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.id='1'
查询配置库中配置项对应的用户组
select reponame,authitem,groupname,authtype from auth_groups cross join groups,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.id='1'
**/

/** 查询配置库对应的用户权限
select reponame,authitem,username,authtype from auth_users cross join users,repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.id='1' order by reponame,authitem,username,authtype
查询配置库对应的用户组权限
select reponame,authitem,groupname,authtype from auth_groups cross join groups,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.id = '1' order by reponame,authitem,groupname,authtype
查询配置库对应的组所包含的用户
select groupname,username from auth_groups cross join uig,groups,users,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and uig.user_id = users.id and uig.group_id = groups.id order by reponame,username
**/