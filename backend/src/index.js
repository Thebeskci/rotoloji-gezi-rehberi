'use strict';

const PUBLIC_ACTIONS = [
  'api::city.city.find',
  'api::city.city.findOne',
  'api::place.place.find',
  'api::place.place.findOne',
];

const AUTHENTICATED_ACTIONS = [
  'api::city.city.find',
  'api::city.city.findOne',
  'api::city.city.create',
  'api::city.city.update',
  'api::place.place.find',
  'api::place.place.findOne',
  'api::place.place.create',
  'api::place.place.update',
  'plugin::upload.content-api.upload',
  'plugin::upload.content-api.find',
  'plugin::upload.content-api.findOne',
];

const ensurePermission = async (strapi, roleId, action) => {
  const existing = await strapi.db.query('plugin::users-permissions.permission').findOne({
    where: {
      action,
      role: roleId,
    },
  });

  if (!existing) {
    await strapi.db.query('plugin::users-permissions.permission').create({
      data: {
        action,
        role: roleId,
      },
    });
  }
};

const ensureRolePermissions = async (strapi, roleType, actions) => {
  const role = await strapi.db.query('plugin::users-permissions.role').findOne({
    where: { type: roleType },
  });

  if (!role) {
    return;
  }

  for (const action of actions) {
    await ensurePermission(strapi, role.id, action);
  }
};

const ensureLocales = async (strapi) => {
  const localesService = strapi.plugin('i18n').service('locales');
  const locales = [
    { code: 'tr', name: 'Turkish (tr)' },
    { code: 'en', name: 'English (en)' },
  ];

  for (const locale of locales) {
    const existing = await localesService.findByCode(locale.code);

    if (!existing) {
      await localesService.create(locale);
    }
  }

  const defaultLocale = await localesService.getDefaultLocale();

  if (defaultLocale !== 'tr') {
    await localesService.setDefaultLocale({ code: 'tr' });
  }
};

const ensureIngestUser = async (strapi) => {
  const email = process.env.INGEST_USER_EMAIL;
  const username = process.env.INGEST_USER_USERNAME || 'rotayz-ingest';
  const password = process.env.INGEST_USER_PASSWORD;

  if (!email || !password) {
    return;
  }

  const authenticatedRole = await strapi.db.query('plugin::users-permissions.role').findOne({
    where: { type: 'authenticated' },
  });

  if (!authenticatedRole) {
    return;
  }

  const existing = await strapi.db.query('plugin::users-permissions.user').findOne({
    where: { email },
  });

  const userService = strapi.plugin('users-permissions').service('user');
  const payload = {
    username,
    email,
    password,
    provider: 'local',
    confirmed: true,
    blocked: false,
    role: authenticatedRole.id,
  };

  if (!existing) {
    await userService.add(payload);
    return;
  }

  await userService.edit(existing.id, payload);
};

module.exports = {
  /**
   * An asynchronous register function that runs before
   * your application is initialized.
   *
   * This gives you an opportunity to extend code.
   */
  register(/*{ strapi }*/) {},

  /**
   * An asynchronous bootstrap function that runs before
   * your application gets started.
   *
   * This gives you an opportunity to set up your data model,
   * run jobs, or perform some special logic.
   */
  async bootstrap({ strapi }) {
    if (process.env.SKIP_PROJECT_BOOTSTRAP === 'true') {
      return;
    }

    await ensureLocales(strapi);
    await ensureRolePermissions(strapi, 'public', PUBLIC_ACTIONS);
    await ensureRolePermissions(strapi, 'authenticated', AUTHENTICATED_ACTIONS);
    await ensureIngestUser(strapi);
  },
};
