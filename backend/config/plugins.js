module.exports = ({ env }) => ({
  upload: {
    config: {
      providerOptions: {
        localServer: {
          maxage: 300000,
        },
      },
      sizeLimit: env.int('UPLOAD_SIZE_LIMIT', 10 * 1024 * 1024),
    },
  },
});
